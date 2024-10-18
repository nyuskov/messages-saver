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
    $('input').on('change', function () {
        $(this).text(escapeHtml($(this).text));
    });

    const socket = new WebSocket('ws://127.0.0.1:8000/mails');

    socket.onmessage = function(event) {
        try {
            let data = JSON.parse(event.data);

            if (data.messages) {
                let messages = data.messages;

                for (let i=0; i<messages.length; ++i) {
                    let message_html = "<div>";
                    message_html += "<p>" + messages[i].message_id + "</p>";
                    message_html += "<p>" + messages[i].subject + "</p>";
                    message_html += "<p>" + messages[i].sended_at + "</p>";
                    message_html += "<p>" + messages[i].received_at + "</p>";
                    message_html += "<p>" + messages[i].text + "</p>";
                    message_html += "</div>";
                    $("#messages").append(message_html);
                }
            } else if (data.progress) {
                $("#progressBar").text(data.progress+"%");
            }
        } catch (e) {
            console.log('Error:', e.message);
        }
    };
    
    setInterval(
        function(){
            socket.send(JSON.stringify({
                message: 'progress'}));
        }, 3000
    );
    
    setInterval(
        function(){
            socket.send(JSON.stringify({
                message: 'messages'}));
        }, 5000
    );
});