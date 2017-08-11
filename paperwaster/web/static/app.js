Vue.component('donate-message', {
    template: `<div>Please consider a
               <a v-bind:href="link" class="btn btn-xs btn-success">small donation</a>
               <transition appear mode="out-in" name="fade">
                 <span v-on:click="updateReason" v-bind:key="reason" class="donation-message"> {{reason}}</span>
               </transition>
               </div>`,
    data: function() {return {
        reason: null
    }},
    computed: {
        link: function () {
            return this.reason ? '/donate' : '/donate?msg=' + encodeURIComponent(this.reason);
        }
    },
    methods: {
        updateReason: function () {
            var reasons = [
                'to help keep things running!',
                'to buy me a drink!',
                'to waste more paper!',
                'to end the war on paper!',
                'to become a meme lord!',
                'to raise your power level to over 9000!',
                'for no particular reason.',
                '...please?',
                'because why not?',
                "because you're awesome!",
                'because the voices told you to...',
            ];
            var reason = reasons[Math.floor(Math.random() * reasons.length)];
            while (reason === this.reason) {
                reason = reasons[Math.floor(Math.random() * reasons.length)];
            }
            this.reason = reason;
        }
    }
});
var vm = new Vue({
    el: '#donateApp',
});

var updateDonationReasonTimer = function() {
vm.$refs.donateMessage.updateReason();
setTimeout(updateDonationReasonTimer, 5*1000);
};
setTimeout(updateDonationReasonTimer, 3*1000);
