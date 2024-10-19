"use strict";

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
    const socket2 = new WebSocket("ws://127.0.0.1:8000/mails");

    socket.onmessage = function (event) {
        try {
            let data = JSON.parse(event.data);

            if (data.messages && data.messages.length) {
                $("#messages tbody").html("");
                let messages = data.messages;
                let nLengthMessages = messages.length;

                for (let i = 0; i < nLengthMessages; ++i) {
                    let message_html = "<tr>";
                    message_html += "<td>" + messages[i].message_id + "</td>";
                    message_html += "<td>" + messages[i].subject + "</td>";
                    message_html += "<td>" + messages[i].sended_at + "</td>";
                    message_html += "<td>" + messages[i].received_at + "</td>";
                    message_html += "<td><p>" + escapeHtml(messages[i].text) + "</p></td>";
                    message_html += "<td>";
                    for (let j = 0; j < messages[i].attachments.length; ++j) {
                        message_html += "<a id='attachment_" + i + "_" + j + "' href='' download='" + messages[i].attachments[j].name + "'>" + messages[i].attachments[j].name + "</a><br>";
                    }
                    message_html += "</td>";
                    message_html += "</tr>";
                    $("#messages tbody").append(message_html);

                    for (let j = 0; j < messages[i].attachments.length; ++j) {
                        let blob = new Blob([messages[i].attachments[j].data], { type: 'application/pdf' });
                        $("#attachment_" + i + "_" + j).attr("href", URL.createObjectURL(blob));
                    }
                }
            } else if (data.progress) {
                $("#progressBar").text(data.progress);
                if (data.progress == "Showing data") {
                    clearInterval(intervalId);
                    socket.send(JSON.stringify({
                        message: "get_messages",
                    }));
                }
            } else if (data.auth_info) {
                intervalId = setInterval(
                    function () {
                        socket2.send(JSON.stringify({
                            message: "progress"
                        }));
                    }, 2000
                );
                socket.send(JSON.stringify({
                    message: "download_messages",
                }));
            }
        } catch (e) {
            console.log("Error:", e.message);
        }
    };

    socket2.onmessage = function (event) {
        try {
            let data = JSON.parse(event.data);
            if (data.progress) {
                $("#progressBar").text(data.progress);
                if (data.progress == "Reading data") {
                    clearInterval(intervalId);
                    socket.send(JSON.stringify({
                        message: "get_messages",
                    }));
                }
            }
        } catch (e) {
            console.log("Error:", e.message);
        }
    };

    let intervalId;
    socket.onopen = function (e) {
        socket.send(JSON.stringify({
            message: "get_auth_info",
        }));
    };
});