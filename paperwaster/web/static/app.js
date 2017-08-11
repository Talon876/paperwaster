Vue.component('donate-message', {
    template: `<div>Please consider a
               <a v-bind:href="link" class="btn btn-xs btn-success">small donation</a>
               <transition mode="out-in" enter-active-class="animated fadeIn" leave-active-class="animated fadeOut" >
                 <span v-on:click="updateReason" v-bind:key="reason" class="donation-message"> {{reason}}</span>
               </transition>
               </div>`,
    props: ['reasons'],
    data: function() {return {
        reason: null
    }},
    computed: {
        link: function () {
            return this.reason === null ? '/donate' : '/donate?msg=' + encodeURIComponent(this.reason);
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
    }
});
var vm = new Vue({
    el: '#donateApp',
});

var updateDonationReasonTimer = function () {
    vm.$refs.donateMessage.updateReason();
    setTimeout(updateDonationReasonTimer, 60 * 1000);
};
setTimeout(updateDonationReasonTimer, 30*1000);
