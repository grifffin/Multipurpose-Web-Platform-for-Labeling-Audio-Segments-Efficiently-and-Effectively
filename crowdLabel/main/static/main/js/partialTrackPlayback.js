var playingIntervalID;

var startTime;
var stopTime;

var current_segment;

document.addEventListener('keydown', function (event) {
    if (event.keyCode === 80) {
        playPause();
    }
});

function playRange(start, stop) {
    pause();
    var audio = document.getElementById("audio");
    audio.currentTime = start;
    stopTime = stop;
    play();
}

function blur() {
    document.activeElement.blur();
}

function changeAudio(filename) {

    $("#audio_source").attr("src", "/media/user_files/" + filename);

    const audio = document.getElementById("audio");
    audio.load();

    pause();
}

/* This was moved to the top of respond_to_study.html -- Only file that uses it */
$(document).ready(function () {
    console.log($("#audio_source").attr("src"));
    getFirstTime();
});


function play() {
    console.log('playable');
    blur();
    var audio = document.getElementById("audio");
    audio.play();
    var button = $("#play_button");
    button.text("Playing");
    button.attr("disabled", "disabled");
    playingIntervalID = setInterval(function () {
        updateTime();
    }, 5);
}

function pause() {
    blur();
    var audio = document.getElementById("audio");
    audio.pause();
    var button = $("#play_button");
    button.text("Play");
    button.removeAttr("disabled");
    clearInterval(playingIntervalID);
}

function updateTime() {

    const audio = document.getElementById("audio");

    //console.log(audio.currentTime);

    if(audio.currentTime > stopTime) {
        pause();
        audio.currentTime = startTime;
        $("#play_button").text("Replay");
        var answers = document.getElementsByClassName("answer");
        for(var i = 0; i < answers.length; ++i) {
            $(answers[i]).removeAttr("disabled");
        }
    }
}

function getFirstTime() {
    console.log('before ajax');
    $.ajax({
        type: 'POST',
        data: {
            //'segment_ajax': false,
            'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val(),
        },
        success: function(data) {
            current_segment = data["seg_id"];
            startTime = data["start"];
            stopTime = data["stop"];
            var filename = data["file_name"];
            changeAudio(filename);
            //console.log("starttime:" + startTime);
            var audio = document.getElementById("audio");
            var my_function = function() {
                audio.currentTime = startTime;
                console.log("currentTime:" + audio.currentTime);
                if(audio.currentTime === startTime) {
                    $("#play_button").removeAttr("disabled");
                    var answers = document.getElementsByClassName("answer");
                    for (var i = 0; i < answers.length; ++i) {
                        $(answers[i]).attr("disabled", "disabled");
                    }
                    audio.removeEventListener("canplay", my_function)
                }
            };
            audio.addEventListener("canplay", my_function);
        },
    });
}

function labelSegment(label_id) {
    $.ajax({
        type: 'POST',
        data: {
            'segment_ajax': true,
            'segment_id': current_segment,
            'label_id': label_id,
            'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val(),
        },
        success: function(data) {
            var answers = document.getElementsByClassName("answer");
            for (var i = 0; i < answers.length; ++i) {
                $(answers[i]).attr("disabled", "disabled");
            }
            current_segment = data["seg_id"];
            startTime = data["start"];
            stopTime = data["stop"];
            var filename = data["file_name"];
            changeAudio(filename);
            //console.log("starttime:" + startTime);
            var audio = document.getElementById("audio");
            var my_function = function() {
                audio.currentTime = startTime;
                console.log("currentTime:" + audio.currentTime);
                if(audio.currentTime === startTime) {
                    $("#play_button").removeAttr("disabled");
                    pause();
                    audio.removeEventListener("canplay", my_function)
                }
            };
            audio.addEventListener("canplay", my_function);
        }
    });

    var url = window.location.href;
    var assignmentIndex = url.search("assignmentId");
    if(assignmentIndex !== -1) {
        var ampIndex = url.substring(assignmentIndex, url.length).indexOf('&');
        var assignmentId = url.substring(assignmentIndex + 13, ampIndex + assignmentIndex);
        console.log(assignmentId);
        $.ajax({
            type: 'POST',
            url: 'https://workersandbox.mturk.com/mturk/externalSubmit',
            data: {
                "assingmentId": assignmentId,
            },
        })
    }
}

