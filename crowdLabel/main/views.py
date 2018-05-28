import json
import random
import string
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse
from django.conf import settings

from main.models import UserType, File, Study, Label, Segment, StudyFile, StudyWorker, Response
from main.forms import DocumentForm

from pydub import AudioSegment


# HOMEPAGE
def index(request):

    if request.is_ajax() and request.user.is_authenticated() and (request.POST.get('btnType') == 'crowd_logout'):
        logout(request)
        data = {'res': 'it worked and auth'}
        return render_to_json_response(data)

    if request.user.is_authenticated():
        # logged in

        # get which type of user is logged in
        user_type = UserType.objects.get(user_id=request.user.id)

        # get name of current user
        fullname = request.user.first_name + ' ' + request.user.last_name
        context = {'full_name': fullname}

        # get the template based on the current user's type (worker or director)
        if user_type.type == 'worker':
            template = loader.get_template('main/home_worker_in.html')
        elif user_type.type == 'director':
            template = loader.get_template('main/home_director_in.html')
        else:
            # this case is here just in case another type is made
            template = loader.get_template('main/home.html')
    else:
        template = loader.get_template('main/home.html')
        context = {}
    return HttpResponse(template.render(context, request))


@csrf_exempt
def crowd_sign_up(request):
    if request.is_ajax():
        user = User.objects.create_user(request.POST.get('email'),
                                        request.POST.get('email'),
                                        request.POST.get('pass'))
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.is_active = True
        user.save()

        if request.POST.get('btnType') == 'create_worker_account':
            type_of_user = 'worker'
        else:
            type_of_user = 'director'

        user_type = UserType(user=user, type=type_of_user)
        user_type.save()

        data = {'res': type_of_user + ' created!'}

        return render_to_json_response(data)

    template = loader.get_template('main/sign_up.html')
    context = {}
    return HttpResponse(template.render(context, request))


@csrf_exempt
def crowd_login(request):

    # true if clicking the login button, false if just visiting the page
    if request.is_ajax():

        # testing the email and password
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(username=email, password=password)

        if user is None:
            # failed login
            data = {'res': 'Incorrect U or P'}
        else:
            # good login
            if user.is_active:
                data = {'res': 'it worked and auth'}
                login(request, user)
                request.session['user_id'] = str(user.id)
                request.session['user_email'] = user.username
                request.session['full_name'] = user.first_name + ' ' + user.last_name

            else:
                data = {'res': 'user inactive - look into more...'}

        # return if it was successful to the client
        return render_to_json_response(data)

    # get the html for the login page
    template = loader.get_template('main/login.html')
    context = {}
    return HttpResponse(template.render(context, request))


def crowd_study_list(request):

    # ensure user is logged in and a director
    if (not request.user.is_authenticated()) or UserType.objects.get(user_id=request.user.id).type != 'director':
        return redirect('/')
    else:
        template = loader.get_template('main/study_list.html')
        fullname = request.user.first_name + ' ' + request.user.last_name  # get name of current user
        user_studies = Study.objects.filter(owner=request.user)
        for study in user_studies:
            segments = Segment.objects.filter(study=study)
            num_responses = len(Response.objects.filter(segment__in=segments))
            completion = float(num_responses) / study.max_total_responses
            study.completion = completion
        context = {'fullname': fullname, 'user_studies': user_studies}
        return HttpResponse(template.render(context, request))


def crowd_assignment_list(request):

    if request.is_ajax():
        code = request.POST.get('code')
        studies = Study.objects.filter(code=code)
        if len(studies) > 0:
            study = studies[0]
            new_study_worker = StudyWorker(study=study, worker=request.user)
            new_study_worker.save()
            data = {'res': 'it worked'}
        else:
            data = {'res': 'no study with that code'}
        # return if it was successful to the client
        return render_to_json_response(data)

    # ensure user is logged in and a worker
    if (not request.user.is_authenticated()) or UserType.objects.get(user_id=request.user.id).type != 'worker':
        return redirect('/')
    else:
        template = loader.get_template('main/study_list_worker.html')
        fullname = request.user.first_name + ' ' + request.user.last_name  # get name of current user

        # There's gotta be a better way
        user_studies = Study.objects.filter(id__in=StudyWorker.objects.filter(worker=request.user).values('study'))

        for user_study in user_studies:
            if user_study.max_responses_per_worker is not None:
                num_responses = len(Response.objects.filter(segment__study=user_study, worker=request.user))
                user_study.remaining_responses = user_study.max_responses_per_worker - num_responses
                if user_study.remaining_responses == 0:
                    user_study.user_status = 'at limit'
                else:
                    user_study.user_status = 'under limit'
            else:
                user_study.user_status = 'no limit'
        context = {'fullname': fullname, 'user_studies': user_studies, 'user_id': request.user.id}
        return HttpResponse(template.render(context, request))


def crowd_new_study(request):

    if request.is_ajax() and UserType.objects.get(user_id=request.user.id).type == 'director':

        # shouldnt you add the condition 'and request.POST.get('btnType') == "create_study"' here?

        # get the attributes of the study (from the fields on the template)
        title = request.POST.get('study_title')
        print(request.POST.get('study_title'))
        labels = request.POST.getlist('labels[]')
        segment_duration = request.POST.get('segment_duration')
        step_size = request.POST.get('step_size')
        max_responses = request.POST.get('max_responses')
        max_segment_responses = request.POST.get('max_segment_responses')
        min_segment_responses = request.POST.get('min_segment_responses')
        threshold = request.POST.get('threshold')
        file_ids = request.POST.getlist('file_ids[]')

        # generate the random access code for workers to join the study
        code_length = 50
        code = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(code_length))

        # make a new Study using the above (files and labels go into their own tables though) and the current user
        study = Study(title=title, owner=request.user, segment_duration=segment_duration, step_size=step_size,
                      max_total_responses=max_responses, max_responses_per_segment=max_segment_responses,
                      min_responses_per_segment=min_segment_responses, threshold=threshold, code=code)

        study.save()

        # label table
        for label in labels:
            new_label = Label(label_title=label, study=study)
            new_label.save()

        # files and segments
        for file_id in file_ids:
            file = File.objects.get(id=file_id)

            # link the study to each file
            new_study_file = StudyFile(study=study, file=file)
            new_study_file.save()

            # segments
            # get duration of file
            sound = AudioSegment.from_file(file.file.path, format="wav")

            duration_in_seconds = len(sound)//1000
            # print(duration_in_seconds)
            start_times = [x * float(study.step_size) for x in range(0, duration_in_seconds)]
            # print(start_times)
            for i in start_times:
                if (i + float(study.segment_duration)) < duration_in_seconds:
                    new_seg = Segment(start=i,
                                      stop=i + float(study.segment_duration),
                                      duration=study.segment_duration,
                                      study=study,
                                      file=file,
                                      status='low_priority')
                    new_seg.save()

        data = {'res': 'it worked'}

        # return if it was successful to the client
        return render_to_json_response(data)

    # ensure user is logged in and a director
    if (not request.user.is_authenticated()) or UserType.objects.get(user_id=request.user.id).type != 'director':
        return redirect('/')
    else:
        user_files = File.objects.filter(uploader=request.user)
        template = loader.get_template('main/create_study.html')
        fullname = request.user.first_name + ' ' + request.user.last_name  # get name of current user
        context = {'fullname': fullname, 'user_files': user_files}
        return HttpResponse(template.render(context, request))


def crowd_upload_files(request):

    # Handle file delete
    if request.is_ajax():
        file = File.objects.get(id=request.POST.get('file_id'))
        file.delete()
        data = {'res': 'file deleted'}
        # return if it was successful to the client
        return render_to_json_response(data)

    # Handle file upload
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            filename = request.FILES['docfile'].name
            docfile = request.FILES['docfile']
            new_file = File(filename=filename, uploader=request.user, file=docfile)
            new_file.save()

            # Redirect to the document list after POST
            return HttpResponseRedirect(reverse('crowd_upload_files'))

    # redirect to homepage if they're not logged in
    if (not request.user.is_authenticated()) or UserType.objects.get(user_id=request.user.id).type != 'director':
        return redirect('/')
    else:
        user_files = File.objects.filter(uploader=request.user)
        form = DocumentForm()
        fullname = request.user.first_name + ' ' + request.user.last_name  # get user's fullname
        template = loader.get_template('main/upload_files.html')
        context = {'fullname': fullname, 'form': form, 'user_files': user_files}
        return HttpResponse(template.render(context, request))


def crowd_respond_to_study(request, study_id):
    # There are two ways the client makes ajax calls. Once at the beginning just to get the first segment,
    # and also after a response is made to record the response AND get a new segment
    if request.is_ajax():

        # This is true if the ajax is returning a response
        if not request.POST.get('segment_ajax') is None:
            seg = Segment.objects.get(id=request.POST.get('segment_id'))
            new_response = Response(segment=seg, user=request.user, label_id=request.POST.get('label_id'))
            new_response.save()
            check_segment(seg)
        prev_responses = list(Response.objects.filter(worker_id=request.user.id).values('segment_id'))
        high_priorities = Segment.objects.filter(study_id=study_id, status='high_priority').exclude(id__in=prev_responses)

        if high_priorities.exists():
            available_segments = high_priorities
        else:
            available_segments = Segment.objects.filter(study_id=study_id, status='low_priority')

        chosen_segment = available_segments[random.randint(0, len(available_segments)-1)]
        data = {
            'seg_id': chosen_segment.id,
            'file_name': chosen_segment.file.filename,
            'start': float(chosen_segment.start),
            'stop': float(chosen_segment.stop),
            'duration': float(chosen_segment.duration),
        }
        return render_to_json_response(data)
    study_worker = StudyWorker.objects.filter(study_id=study_id, worker_id=request.user.id)
    if study_worker is None:
        return redirect('/')
    template = loader.get_template('main/respond_to_study.html')
    labels = Label.objects.filter(study_id=study_id)
    context = {'study': Study.objects.get(id=study_id), 'labels': labels, 'remaining': 17}
    return HttpResponse(template.render(context, request))


def crowd_view_study(request, study_id):
    segments = Segment.objects.filter(study_id=study_id, status__contains='resolved')
    labels = Label.objects.filter(study_id=study_id)
    curr_id = 1
    for segment in segments:
        label_counts = []
        max_label_count = -1
        responses = Response.objects.none()
        for label in labels:
            label_responses = Response.objects.filter(segment=segment, label=label)
            responses |= label_responses
            count = len(label_responses)
            label_counts.append(count)
            if count > max_label_count:
                max_label_count = count
        segment.label_counts = label_counts
        segment.percent = str(int(max_label_count/sum(label_counts) * 100)) + '%'
        segment.local_id = curr_id
        segment.responses = responses
        curr_id += 1
    template = loader.get_template('main/view_study.html')
    context = {'study': Study.objects.get(id=study_id), 'labels': labels, 'segments': segments}
    return HttpResponse(template.render(context, request))


def check_segment(segment):
    responses = Response.objects.filter(segment=segment)
    if responses.exists():
        min_responses = Study.objects.get(id=segment.study.id).min_responses_per_segment
        max_responses = Study.objects.get(id=segment.study.id).max_responses_per_segment
        threshold = Study.objects.get(id=segment.study.id).threshold
        if len(responses) < min_responses:
            segment.status = 'high_priority'
            segment.save()
            print('segment made high priority')
        else:
            labels = list(responses.values('label').distinct())
            max_num_responses = 0
            max_label_id = None
            for label in labels:
                print(label['label'])
                num_responses = len(responses.filter(label_id=label['label']))
                if num_responses > max_num_responses:
                    max_num_responses = num_responses
                    max_label_id = label['label']
            if (float(max_num_responses) / float(len(responses))) > (float(threshold) / float(100)):
                segment.status = 'resolved_good'
                segment.final_label_id = max_label_id
                segment.save()
            elif len(responses) >= max_responses:
                segment.status = 'resolved_bad'
                segment.save()


def render_to_json_response(context, **response_kwargs):
    data = json.dumps(context)
    response_kwargs['content_type'] = 'application/json'
    return HttpResponse(data, **response_kwargs)
