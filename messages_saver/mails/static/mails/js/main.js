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

    socket.onopen = function(e) {
        socket.send(JSON.stringify({
            message: 'progress'
        }));
        socket.send(JSON.stringify({
            message: 'info'
        }));
        socket.send(JSON.stringify({
            message: 'messages'
        }));
    };

    socket.onmessage = function(event) {
        try {
            console.log(event);
        } catch (e) {
            console.log('Error:', e.message);
        }
    };
});