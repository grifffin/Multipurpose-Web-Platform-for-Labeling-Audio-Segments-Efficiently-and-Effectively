
function cosfc_login() {
    $("#new_loader").css({"display": "block"});
    $("body").css({"overflow": "hidden"});

    $.ajax(
        {
            type: "POST",

            data: {
                btnType: 'csci_login',
                email: $('#login-email').val(),
                password: $('#login-pass').val(),
                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
            },

            success: function (data) {
                if (data['res'] === 'it worked and auth') {
                    document.location.href = "/";
                }
                else {
                    $("#new_loader").css({"display": "none"});
                    // show incorrect login info modal
                    $("#modal_feedback").modal("show");

                    setTimeout(function () {
                        window.location.reload();
                    }, 1500);
                }
            }
        });
}

/* Allow user to update password*/
function update_password() {

    $.ajax(
        {
            type: "POST",

            data: {
                btnType: 'update_password',
                password: $('#login-pass-1').val(),
                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
            },
            success: function (data) {

                $("#login-pass-1").prop('disabled', true);
                $("#update_pass_button").prop('disabled', true);
                $("#modal_pass_updated").modal("show");
                setTimeout(function () {
                    $("#modal_pass_updated").modal("hide");
                    document.location.href = "/";
                }, 1200);
            }
        });
}

function cosfc_signup_worker() {
    $("#new_loader").fadeIn();

    first_name = $("#worker_first_name").val();
    last_name = $("#worker_last_name").val();
    email = $("#worker_sign_up_email").val();
    pass = $("#studeint_sign_up_pass").val();

    section = $("#section_list option:selected").text();

    $.ajax(
        {
            type: "POST",

            data: {
                btnType: 'create_worker_account',
                first_name: first_name,
                last_name: last_name,
                email: email,
                pass: pass,
                section: section,
                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
            },
            success: function (data) {
                window.location = '/login';
            }
        });
}

function cosfc_signup_director() {

    $("#new_loader").fadeIn();
    first_name = $("#director_first_name").val();
    last_name = $("#director_last_name").val();
    institution = $("#director_institution").val();
    email = $("#director_sign_up_email").val();
    pass = $("#director_sign_up_pass").val();

    $.ajax(
        {
            type: "POST",

            data: {
                btnType: 'create_director_account',
                first_name: first_name,
                last_name: last_name,
                institution: institution,
                email: email,
                pass: pass,
                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
            },
            success: function (data) {
                $("#new_loader").fadeOut();
                $("#modal_account_created_director").modal("show");
            }
        });
}

function csci_logout() {
    $("#new_loader").css({"display": "block"});
    $("body").css({"overflow": "hidden"});

    $.ajax(
        {
            type: "POST",

            data: {
                btnType: 'crowd_logout',
                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
            },
            success: function (data) {
                location.reload();
            }
        });
}

function switch_to_worker_sign_up() {
    $("#btn_switch_to_worker").fadeOut();

    $("#director_sign_up_div").fadeOut(function () {
        $("#worker_sign_up_div").fadeIn();
        $("#btn_switch_to_director").fadeIn();
    });
}

function switch_to_director_sign_up() {

    $("#btn_switch_to_director").fadeOut();

    $("#worker_sign_up_div").fadeOut(function () {
        $("#director_sign_up_div").fadeIn();
        $("#btn_switch_to_worker").fadeIn();

        $("#director_first_name").focus();
    });
}

function delete_file(button) {
    console.log(button);
    var file_id = button.id.split('_')[0];

    $.ajax(
        {
            type: "POST",

            data: {
                btnType: 'delete_file',
                file_id: file_id,
                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
            },
            success: function (data) {
                location.reload();
            }
        });
}

function makeLabelBoxesModal() {
    var number = document.getElementById("label_number_box").value;
    var labels = document.getElementById("labels_list");

    for (i = 0; i < number; ++i) {
        var node = document.createElement("input");
        $(node).css({"font-size:": "20px", "text-align":"center"});
        node.type = "text";
        node.className = ".label_box";
        node.placeholder = "Label " + (i+1);
        labels.appendChild(node);
    }

    $("#label_modal").modal('show');

}

function alterLabelBoxesModal() {
    var number = document.getElementById("label_number_box_modal").value;
    var labels = document.getElementById("labels_list");
    $(labels).empty();
    for (i = 0; i < number; ++i) {
        var node = document.createElement("input");
        $(node).css({"font-size:": "20px", "text-align":"center"});
        node.type = "text";
        node.className = ".label_box";
        node.placeholder = "Label " + (i+1);
        labels.appendChild(node);
    }


}

function makeLabelBoxes() {
    var number = document.getElementById("label_number_box").value;
    var container = document.getElementById("label_boxes");
    if(number === '') {
        container.innerHTML = "Enter the number of labels"
    } else {

        container.innerHTML = '';

        for (i = 0; i < number; ++i) {
            var label = document.createElement("label");
            label.textContent = "Label " + (i + 1) + ":";
            label.className = "label_label";
            container.appendChild(label);
            var box = document.createElement("input");
            box.type = "text";
            box.className = "label_box";
            container.appendChild(box);
            container.appendChild(document.createElement("br"))
        }
    }
}

function saveLabels(){

    var labels = document.getElementById("labels_list").childNodes;
    var saved_labels = document.getElementById("saved_labels");
    $(saved_labels).empty();
    console.log(labels);
    for (var i = 0; i < labels.length; i++) {
        var newLabel = document.createElement("div");
        if (labels[i].value !== undefined) {
            newLabel.innerText = labels[i].value;
            $(newLabel).css({'font-size': '13px'});
            saved_labels.appendChild(newLabel);
        }
    }
    $("#label_modal").modal('hide');
}

function explain_responses() {
    var min = document.getElementById("min_segment_response_box").value;
    var max = document.getElementById("max_segment_response_box").value;
    var threshold = document.getElementById("threshold_response_box").value;
    if(!isNaN(min) && !isNaN(max) && !isNaN(threshold)) {
        var requirements = [];
        var possibilities = [];
        var container = document.getElementById("response_explanation");
        container.innerHTML = "";
        for(var i = parseInt(min); i <= parseInt(max); i++) {
            requirements.push(Math.ceil(i * parseFloat(threshold) / 100));
            if(i > min) {
                possibilities.push(requirements[i-min] <= requirements[i-min-1])
            } else {
                possibilities.push(true)
            }
            var span = document.createElement("span");
            span.textContent = "Stop at " + i + " if at least " + requirements[i-min] + " agree";
            $(span).css("color",possibilities[i-min] ? "black" : "lightgray");
            container.appendChild(span);
            container.appendChild(document.createElement("br"));
        }
    }
}

function createStudy() {
    var title = document.getElementById("title_box").value;
    console.log(title);
    var labels = [];
    var saved_labels = document.getElementsByClassName("label_box");
    for(var i = 0; i < saved_labels.length; ++i) {
        labels.push(saved_labels[i].value);
    }
    var file_ids = [];
    var file_check_boxes = document.getElementsByClassName("file_check_box");
    for(i = 0; i < file_check_boxes.length; ++i) {
        if(file_check_boxes[i].checked) {
            var file_id = file_check_boxes[i].id.split('_')[0];
            file_ids.push(file_id);
        }
    }
    var segment_duration = document.getElementById("segment_duration_response_box").value;
    var step_size = document.getElementById("step_size_response_box").value;
    var max_responses = document.getElementById("max_response_box").value;
    var max_segment_responses = document.getElementById("max_segment_response_box").value;
    var min_segment_responses = document.getElementById("min_segment_response_box").value;
    var threshold = document.getElementById("threshold_response_box").value;

    $.ajax(
        {
            type: "POST",

            data: {
                btnType: 'create_study',
                study_title: title,
                'labels[]': labels,
                segment_duration: segment_duration,
                step_size: step_size,
                max_responses: max_responses,
                max_segment_responses: max_segment_responses,
                min_segment_responses: min_segment_responses,
                threshold: threshold,
                'file_ids[]': file_ids,

                csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
            },
            success: function (data) {
                 $("#create_study_success_modal").modal("show");
                        setTimeout(function () {
                            $("create_study_success_modal").modal("hide");
                            location.reload();
                        }, 1000);
            }
        });
}

function join_study_button_click() {
    var field = document.getElementById("join_study_field");
    console.log(field);
    if(field.style.display === "none") {
        field.style.display = "block";
        var button = document.getElementById("join_study_button");
        button.textContent = "JOIN"
    } else {
        var code = field.value;
        $.ajax(
            {
                type: "POST",

                data: {
                    btn_type: "join_study",
                    code: code,

                    csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
                },
                success: function (data) {
                    location.reload();
                }
            }
        )
    }
}

function download_csv() {
    //the file's contents
    var out = "";
    var top_row = document.getElementById("header_row");
    var rows = Array.from(document.getElementsByClassName("view"));
    //add top_row to the beginning of rows
    rows.unshift(top_row);
    for(var i = 0; i < rows.length; ++i) {
        var row_data = rows[i].childNodes;
        //row_data.length - 2 to avoid the play column
        for(var j = 0; j < row_data.length - 2; ++j) {
            if(row_data[j].nodeName === "TD" || row_data[j].nodeName === "TH") {
                out += $(row_data[j]).text().trim();
                out += ", "
            }
        }
        out += '\n';
    }
    var a = document.getElementById("a");

    var file = new Blob([out], {type: 'text/plain'});
    a.href = URL.createObjectURL(file);
    a.download = "results_" + $("#title").text() + ".csv";

    a.click();
}
