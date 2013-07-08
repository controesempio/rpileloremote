from flask import Flask, request, g, jsonify
from Queue import Queue
import os, math

from rpileloremote.lelo import LeloRemote
from rpileloremote.json2iter import JSON2Iters


class VibeFlask(Flask):
    def run(self,debug=False, *args,**kargs):
        #        if not debug or (os.environ.get('WERKZEUG_RUN_MAIN') == 'true'):
        self.lelo = LeloRemote(Queue())
        self.lelo.daemon = True
        self.lelo.start()
        Flask.run(self,debug=debug,*args,**kargs)

app = VibeFlask(__name__)

@app.route('/',methods=['GET','POST'])
def info():
    if request.method == 'POST':
        new_iterator = JSON2Iters().parse(request.data)
        if new_iterator:
            app.lelo.put(new_iterator)
        else:
            abort(500)
    return jsonify({'strength': app.lelo.strength , 'timeout': app.lelo.timeout, 'queue_length' : app.lelo.queue.qsize()})

if __name__ == '__main__':
    app.run(debug=True,use_reloader=False,host='0.0.0.0',port=80)
