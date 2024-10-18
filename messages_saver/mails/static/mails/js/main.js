"use strict";

let last_message_id;

function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

$(document).ready(function () {
    $("input").on("change", function () {
        $(this).text(escapeHtml($(this).text));
    });

    const socket = new WebSocket("ws://127.0.0.1:8000/mails");

    socket.onmessage = function (event) {
        try {
            let data = JSON.parse(event.data);

            if (data.messages && data.messages.length) {
                let messages = data.messages;
                let nLengthMessages = messages.length;
                last_message_id = messages[nLengthMessages - 1].id;

                for (let i = 0; i < nLengthMessages; ++i) {
                    let message_html = "<tr>";
                    message_html += "<td>" + messages[i].message_id + "</td>";
                    message_html += "<td>" + messages[i].subject + "</td>";
                    message_html += "<td>" + messages[i].sended_at + "</td>";
                    message_html += "<td>" + messages[i].received_at + "</td>";
                    message_html += "<td>" + messages[i].text + "</td>";
                    message_html += "<td>";
                    for (let j = 0; j < messages[i].attachments.length; ++j) {
                        message_html += "<a id='attachment_" + i + "_" + j + "' href='' download='" + messages[i].attachments[j].name + "'>" + messages[i].attachments[j].name + "</a>";
                    }
                    message_html += "</td>";
                    message_html += "</tr>";
                    $("#messages").append(message_html);

                    for (let j = 0; j < messages[i].attachments.length; ++j) {
                        let blob = new Blob([messages[i].attachments[j].data], {type: 'application/pdf'});
                        $("#attachment_" + i + "_" + j).attr("href", URL.createObjectURL(blob));
                    }
                }
            } else if (data.progress) {
                $("#progressBar").text(data.progress + "%");
            }
        } catch (e) {
            console.log("Error:", e.message);
        }
    };

    setInterval(
        function () {
            socket.send(JSON.stringify({
                message: "progress"
            }));
        }, 3000
    );

    setInterval(
        function () {
            socket.send(JSON.stringify({
                message: "messages",
                last_message_id: last_message_id
            }));
        }, 5000
    );
});