paper.install(window);
Math.clamp = function(val,min,max){return Math.max(min,Math.min(max,val));}

toastr.options = {
  closeButton: true,
  showDuration: 300,
  timeOut: 1500,
  positionClass: 'toast-top-full-width',
  preventDuplicates: true,
};

Vue.component('fading-message', {
    template: `
    <div style="display:inline-block">
        <transition mode="out-in" enter-active-class="animated fadeIn" leave-active-class="animated fadeOut">
            <span :key="message" class="donation-message">{{message}}</span>
        </transition>
    </div>`,
    props: ['message']
});

Vue.component('donate-message', {
    template: `<div>
                 Please consider a <a :href="link" class="btn btn-xs btn-success">small donation </a>
                 <fading-message class="donation-message" @click.native="updateReason(true)" :message="reason"/>
               </div>`,
    props: ['reasons', 'delay', 'initialDelay', 'donateUrl'],
    data: function() {return {
        reason: null
    }},
    computed: {
        link: function () {
            return this.reason === null ?
                   this.donateUrl : this.donateUrl + '?msg=' + encodeURIComponent(this.reason);
        }
    },
    methods: {
        updateReason: function (fun) {
            if (fun && this.reason && this.reason.includes('over 9000')) {
                over9000.play();
            }
            var reason = this.reasons[Math.floor(Math.random() * this.reasons.length)];
            while (reason === this.reason) {
                reason = this.reasons[Math.floor(Math.random() * this.reasons.length)];
            }
            this.reason = reason;
        }
    },
    created: function() {
        var self = this;
        var updateReasonLoop = function() {
            self.updateReason();
            setTimeout(updateReasonLoop, self.delay);
        };
        setTimeout(updateReasonLoop, this.initialDelay);
    }
});

var state = {
    showStream: window.localStorage['showStream'] === undefined ? true : JSON.parse(window.localStorage['showStream'])
};
Vue.component('twitch-stream', {
    template: `
    <div>
    <div class="row text-center bottom-buffer">
        <div class="col-lg-12">
            <button @click="toggleStream" class="btn btn-xs btn-info btn pull-right">
            <span :class="['glyphicon', icon]"></span>
            {{this.show?'Hide':'Show'}} Stream 
            </button>
        </div>
    </div>
    <transition leave-active-class="animated slideOutRight">
    <div class="row bottom-buffer" v-if="show">
        <div class="col-lg-8">
            <div class="embed-responsive embed-responsive-16by9">
                <iframe @load="ready('stream')"
                        :style="{opacity: this.streamReady?1:0}"
                        :src="'https://player.twitch.tv/?channel=' + this.username"
                        class="embed-responsive-item slow-fade" allowfullscreen="true" scrolling="no"></iframe>
                <div style="{opacity: this.streamReady?0:1, border: '1px solid black', width: '300px', height: '200px'">
                </div>
            </div>
        </div>
        <div class="col-lg-4">
            <div class="embed-responsive embed-responsive-4by3 chat-embed">
                <iframe @load="ready('chat')"
                        :style="{opacity: this.chatReady?1:0}"
                        :src="'https://www.twitch.tv/' + this.username + '/chat?popout='"
                        class="embed-responsive-item slow-fade" allowfullscreen="true" scrolling="no"></iframe>
            </div>
        </div>
    </div>
    </transition>
    </div>`,
    props: ['username'],
    data: function() {return {
        show: window.localStorage['showStream'] === undefined ? true : JSON.parse(window.localStorage['showStream']),
        streamReady: false,
        chatReady: false,
    }},
    computed: {
        icon: function () {
            return this.showStream ? 'glyphicon-eye-close' : 'glyphicon-eye-open';
        },
    },
    methods: {
        toggleStream: function() {
            this.show = !this.show;
            window.localStorage['showStream'] = JSON.stringify(this.show);
            if (!this.showStream) {
                this.streamReady = false;
                this.chatRead = false;
            }
        },
        ready: function(what) {
            if (what === 'stream') {
                this.streamReady = true;
            } else if (what === 'chat') {
                this.chatReady = true;
            }
        },
    }
});

Vue.component('message-form', {
    template: `
    <div class="input-group input-group-lg">
        <select v-model="fontSize" style="width:15%"
                class="selectpicker form-control" title="Select Text Size">
            <option disabled :value="null">Text Size</option>
            <option :style="{fontSize: fs.size + 'px'}" v-for="fs in fontSizes" :value="fs.value">{{fs.label}}</option>
        </select>
        <input v-model="message" @keyup.enter="printMessage"
               style="width:85%" autofocus autcomplete="off" type="text"
               maxlength="160" class="form-control input-lg" placeholder="Print a message...">
        <span class="input-group-btn">
            <button @click="printMessage" class="btn btn-primary btn-lg" type="submit">
                <span class="glyphicon glyphicon-print right-buffer"></span> Print
            </button>
        </span>
    </div>`,
    props: ['fontSizes'],
    data: function() {return {
        message: null,
        fontSize: null,
    }},
    methods: {
        printMessage: function() {
            if (this.message) {
                var fontSize = this.fontSize || 'medium';
                var self = this;
                console.log('Printing size ' + fontSize + ': ' + this.message);
                axios.post('/send-message', {msg: this.message, size: fontSize})
                    .then(function(resp) {
                        if (resp.status == 200) {
                            toastr.info('Printing message...');
                            self.message = null;
                        }                    })
                    .catch(function(err) {
                        if (err.response.status == 429) {
                            var seconds = err.response.headers['retry-after'];
                            var suffix = (seconds <= 1 ? ' 1 second!' : seconds + ' seconds!');
                            toastr.error('Whoa there - try again in ' + suffix);
                        } else {
                            toastr.error(err.response.data.error, 'Oh noez!');
                        }
                        self.sending = false;
                    });
            }
        }
    }
});

var bitmap = [];

Vue.component('image-form', {
    template: `
    <div>
    <div class="row bottom-buffer text-center">
        <div class="col-lg-12">
            <div class="btn-group" role="group">
                <a class="btn btn-lg btn-warning" @click.prevent="clear(true)">
                    <span class="glyphicon glyphicon-trash right-buffer"></span>Clear
                </a>
                <a :class="{'disabled': this.sending}" class="btn btn-lg btn-primary" @click.prevent="printImage">
                    <span class="glyphicon glyphicon-print right-buffer"></span> Print
                </a>
            </div>
        </div>
    </div>

    <div class="row text-center bottom-buffer">
        <div class="col-lg-12">
            <canvas v-once style="border: 1px solid black"
                    @contextmenu.prevent
                    ref="drawingArea"
                    :width="width" :height="height"></canvas>
        </div>
    </div>
    </div>
    `,
    data: function() {return {
        pencil: null,
        pixelSize: 16,
        width: 768,
        height: 768,
        sending: false,
        lastPoint: null,
        dragging: null
    }},
    methods: {
        pack: function() {
            var self = this;
            var data = [];
            bitmap.forEach(function (row, y) {
                row.forEach(function (col, x) {
                    var pixel = bitmap[y][x];
                    data.push(pixel.value);
                });
            });

            var imageString = data.join('');
            var chunks = imageString.match(/.{1,32}/g);
            var packedChunks = chunks ? chunks.map(function (chunk) {
                var binaryNum = parseInt(chunk, 2);
                var decimalNum = binaryNum.toString(16);
                return decimalNum;
            }) : [];
            return packedChunks.join('-');

        },
        isImageEmpty: function() {
            var self = this;
            var isEmpty = true;
            bitmap.forEach(function (row, y) {
                row.forEach(function (col, x) {
                    var pixel = bitmap[y][x];
                    if (pixel.value !== 0) {
                        isEmpty = false;
                    }
                });
            });
            return isEmpty;
        },
        clear: function(showToast) {
            if (showToast) {
                toastr.warning('Ka-Boom!', { showDuration: 300, timeout: 500 });
            }
            var self = this;
            bitmap.forEach(function (row, y) {
                row.forEach(function (col, x) {
                    var pixel = bitmap[y][x];
                    pixel.rect.fillColor = 'white';
                    pixel.value = 0;
                });
            });
        },
        printImage: function() {
            var self = this;
            if (!this.isImageEmpty()) {
                this.sending = true;
                axios.post('/send-image', {code: this.pack()})
                    .then(function(resp) {
                        if (resp.status == 200) {
                            toastr.info('Printing image...');
                            self.clear(false);
                        }
                        self.sending = false;
                    })
                    .catch(function(err) {
                        if (err.response.status == 429) {
                            var seconds = err.response.headers['retry-after'];
                            var suffix = (seconds <= 1 ? ' 1 second!' : seconds + ' seconds!');
                            toastr.error('Whoa there - try again in ' + suffix);
                        } else {
                            toastr.error(err.response.data.error, 'Oh noez!');
                        }
                        self.sending = false;
                    });
            }
        },
        createIndicator: function () {
            var indicator = new Path.Rectangle([0, 0], [this.pixelSize, this.pixelSize]);
            indicator.fillColor = new Color(1, 1, 0, 0.5);
            indicator.strokeColor = 'black';
            indicator.strokeWidth = 2;
            return indicator;
        },
        createPencil: function (indicator) {
            var self = this;
            pencil = new Tool();
            pencil.onMouseDown = function (event) {
                var tilePoint = self.toTile(event.point);
                indicator.position = tilePoint.position;
                var pixel = bitmap[tilePoint.tY][tilePoint.tX];

                if (event.event.which === 0 || event.event.which === 1) {
                    pixel.rect.fillColor = 'black';
                    pixel.value = 1;
                } else if (event.event.which === 3) {
                    pixel.rect.fillColor = 'white';
                    pixel.value = 0;
                }
            };
            var doLineDrawing = function(x0, y0, x1, y1, event) {
                var steep = false;
                if (Math.abs(x0 - x1) < Math.abs(y0 - y1)) {
                    [x0, y0] = [y0, x0];
                    [x1, y1] = [y1, x1];
                    steep = true;
                }
                if (x0 > x1) {
                    [x0, x1] = [x1, x0];
                    [y0, y1] = [y1, y0];
                }
                var dx = x1 - x0;
                var dy = y1 - y0;

                var derror2 = Math.abs(dy)*2;
                var error2 = 0;
                var y = y0;

                for (var x = x0; x <= x1; x++) {
                    var pixel = steep?bitmap[x][y]:bitmap[y][x];
                    if (event.event.which === 0 || event.event.which === 1) {
                        pixel.rect.fillColor = 'black';
                        pixel.value = 1;
                    } else if (event.event.which === 3) {
                        pixel.rect.fillColor = 'white';
                        pixel.value = 0;
                    }
                    error2 += derror2;
                    if (error2 > dx) {
                        y += (y1>y0 ? 1 : -1);
                        error2 -= dx*2;
                    }
                }
            };
            pencil.onMouseDrag = function (event) {
                pencil.onMouseDown(event);
                var tilePoint = self.toTile(event.point);
                if (this.lastPoint) {
                    doLineDrawing(this.lastPoint.tX, this.lastPoint.tY, tilePoint.tX, tilePoint.tY, event);
                }
                this.lastPoint = tilePoint;
            };
            pencil.onMouseUp = function (event) {
                indicator.bringToFront();
                this.lastPoint = null;
            };
            pencil.onMouseMove = function (event) {
                var tilePoint = self.toTile(event.point);
                indicator.position = tilePoint.position;
            };
        },
        toTile: function (point) {
            var tx = Math.clamp(Math.floor(point.x / this.pixelSize), 0, paper.view.viewSize.width / this.pixelSize - 1);
            var ty = Math.clamp(Math.floor(point.y / this.pixelSize), 0, paper.view.viewSize.height / this.pixelSize - 1);
            return {
                tX: tx,
                tY: ty,
                position: [tx * this.pixelSize + this.pixelSize / 2,
                ty * this.pixelSize + this.pixelSize / 2]
            }
        }
    },
    mounted: function() {
        var width = this.width / this.pixelSize;
        var height = this.height / this.pixelSize;
        paper.setup(this.$refs.drawingArea);
        paper.view.viewSize = [this.width, this.height];
        var indicator = this.createIndicator()
        this.pencil = this.createPencil(indicator);

        for (var row = 0; row < height; row++) {
            var line = [];
            for (var col = 0; col < width; col++) {
                var rect = new Path.Rectangle([col * this.pixelSize, row * this.pixelSize], [this.pixelSize, this.pixelSize]);
                line.push({ rect: rect, value: 0 });
            }
            bitmap.push(line);
        }
        pencil.activate();
        paper.view.draw();
    }
});

new Vue({
    el: '#donateApp',
});
var over9000 = new Howl({
    src: ['/static/9000.ogg'],
    volume: 0.35
});
