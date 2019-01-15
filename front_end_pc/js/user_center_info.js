var vm = new Vue({
    el: '#app',
    data: {
        host,
        user_id: sessionStorage.user_id || localStorage.user_id,
        token: sessionStorage.token || localStorage.token,
        username: '',
        mobile: '',
        email: '',
        email_active: false,
        set_email: false,
        send_email_btn_disabled: false,
        send_email_tip: '重新发送验证邮件',
        email_error: false,
        histories: []
    },

    mounted: function () {
        // 1. 获取用户个人信息
        
        // 2. 补充请求浏览历史
    },

    methods: {
        // 退出
        logout: function () {
            sessionStorage.clear();
            localStorage.clear();
            location.href = '/login.html';
        },

        check_email: function () {
            var re = /^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$/;
            if (re.test(this.email)) {
                this.email_error = false;
            } else {
                this.email_error = true;
            }
        },

        // 保存email
        save_email: function () {
            
        }
    }
});


