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
                 <fading-message class="donation-message" @click.native="updateReason" :message="reason"/>
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
        updateReason: function () {
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
