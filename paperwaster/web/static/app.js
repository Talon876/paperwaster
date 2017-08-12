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

new Vue({
    el: '#donateApp',
});
