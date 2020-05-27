import os
import http.server
import telebot
from bot import bot

if not os.getenv('HEROKU'):
    if os.getenv('PROXY'):
        telebot.apihelper.proxy = {'https': os.getenv('PROXY')}
    bot.remove_webhook()
    bot.polling()
    bot.set_webhook(os.getenv('APP_URL'))
else:
    class Handler(http.server.BaseHTTPRequestHandler):
        def do_post(self):
            self.send_response(200)
            self.end_headers()
            content_length = int(self.headers['Content-Length'])
            content = self.rfile.read(content_length).decode('utf-8')

            update = telebot.types.Update.de_json(content)
            bot.process_new_messages([update.message])

    bot.set_webhook(os.getenv('APP_URL'))
    server_address = ('0.0.0.0', int(os.getenv('PORT') or 5000))
    server = http.server.HTTPServer(server_address, Handler)
    server.serve_forever()
