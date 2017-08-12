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

Vue.component('twitch-stream', {
    template: `
    <div>
    <div class="row text-center bottom-buffer">
        <div class="col-lg-12">
            <button @click="toggleStream" class="btn btn-xs btn-info btn pull-right">
            <span :class="['glyphicon', icon]"></span>
            {{this.showStream?'Hide':'Show'}} Stream 
            </button>
        </div>
    </div>
    <transition leave-active-class="animated slideOutRight">
    <div class="row bottom-buffer" v-if="showStream">
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
        showStream: true,
        streamReady: false,
        chatReady: false,
    }},
    computed: {
        icon: function() {
            return this.showStream ? 'glyphicon-eye-close':'glyphicon-eye-open';
        }
    },
    methods: {
        toggleStream: function() {
            this.showStream = !this.showStream;
            if (!this.showStream) {
                this.streamReady = false;
                this.chatRead = false;
            }
        },
        ready: function(what) {
            console.log(what + ' is ready');
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
                $.ajax({
                    type: 'POST',
                    url: '/send-message',
                    data: JSON.stringify({ msg: this.message, size: fontSize }),
                    contentType: 'application/json',
                    complete: function (xhr, status) {
                        if (xhr.status == 200) {
                            toastr.info('Printing message...');
                            self.message = null;
                        } else if (xhr.status == 429) {
                            var seconds = xhr.getResponseHeader('Retry-After');
                            var suffix = (seconds <= 1 ? ' 1 second!' : seconds + ' seconds!');
                            toastr.error('Whoa there - try again in ' + suffix);
                        } else {
                            toastr.error(xhr.responseJSON.error, 'Oh noez!');
                        }
                    }
                });
            }
        }
    }
});

new Vue({
    el: '#donateApp',
});
var over9000 = new Howl({
    src: ['/static/9000.ogg'],
    volume: 0.35
});
