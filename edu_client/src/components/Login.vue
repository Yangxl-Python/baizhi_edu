<template>
  <div class="login box">
    <img src="../../static/image/5c8877290ad55.png" alt="">
    <div class="login">
      <div class="login-title">
        <img src="../../static/image/logo.png" alt="">
        <p>百知教育给你最优质的学习体验!</p>
      </div>
      <div class="login_box">
        <div class="title">
          <span @click="pwd_login=true" :class="pwd_login?selected:''">密码登录</span>
          <span @click="pwd_login=false" :class="pwd_login?'':selected">短信登录</span>
        </div>
        <div class="inp" v-show="pwd_login">
          <input type="text" placeholder="用户名 / 手机号码 / 邮箱" class="user" v-model="account">
          <input type="password" name="" class="pwd" placeholder="密码" v-model="pwd">
          <div id="geetest1"></div>
          <div class="rember">
            <p>
              <input type="checkbox" class="no" v-model="remember_me"/>
              <span>记住密码</span>
            </p>
            <p>忘记密码</p>
          </div>
          <button class="login_btn btn btn-primary" @click="get_captcha">登录</button>
          <p class="go_login">没有账号
            <router-link to="/register">立即注册</router-link>
          </p>
        </div>
        <div class="inp" v-show="!pwd_login">
          <input type="text" placeholder="手机号码" class="user" v-model="phone">
          <input type="text" class="pwd" placeholder="短信验证码" v-model="code">
          <button id="get_code" class="btn btn-primary" @click="get_code" :disabled="is_send">{{sms_btn}}</button>
          <div class="rember">
            <p>
              <input type="checkbox" class="no" v-model="remember_me"/>
              <span>记住我</span>
            </p>
          </div>
          <button class="login_btn" @click="login_by_phone" :disabled="is_sub">{{login_btn}}</button>
          <p class="go_login">没有账号
            <router-link to="/register">立即注册</router-link>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
  export default {
    name: "Login",
    data() {
      return {
        // 多方式登录
        account: '',
        pwd: '',
        remember_me: false,
        pwd_login: true,
        selected: 'selected',
        phone: '',
        code: '',
        sms_btn: '获取验证码',
        is_send: false,
        is_sub: false,
        login_btn: '登录',
      }
    },
    methods: {
      get_captcha() {
        this.$axios({
          url: this.$settings.HOST + "user/captcha/",
          method: 'get',
          params: {
            username: this.account,
          }
        }).then(response => {
          let data = JSON.parse(response.data);
          initGeetest({
            gt: data.gt,
            challenge: data.challenge,
            product: "popup", // 产品形式，包括：float，embed，popup。注意只对PC版验证码有效
            offline: !data.success, // 表示用户后台检测极验服务器是否宕机，一般不需要关注
            new_captcha: data.new_captcha
          }, this.handlerPopup);
        }).catch(error => {
          console.log(error);
          this.$message.error("用户名或密码错误");
        });
      },
      handlerPopup(captchaObj) {
        // 回调函数中 this指向会被改变成 所以重新赋值
        let self = this;
        captchaObj.onSuccess(function () {
          let validate = captchaObj.getValidate();
          self.$axios({
            url: self.$settings.HOST + "user/captcha/",
            method: "post",
            data: {
              geetest_challenge: validate.geetest_challenge,
              geetest_validate: validate.geetest_validate,
              geetest_seccode: validate.geetest_seccode
            }
          }).then(response => {
            // console.log(response.data.status);
            if (response.data.status) {
              self.user_login();
            }
          }).catch(error => {
            console.log(error);
          });
        });
        // 将生成的验证码添加到 id为geetest1的div中
        document.getElementById("geetest1").innerHTML = "";
        captchaObj.appendTo("#geetest1");
      },
      login_success(res) {
        if (res.status === 200 && res.data.token) {  // 若登录成功则status=200 且有token
          let user_info = {  // 储存用户信息
            'user_id': res.data.user_id,
            'account': this.account,  // 登录时使用的信息（邮箱，手机号，账号）
            'username': res.data.username,  // 用于显示用户名
            'pwd': this.pwd
          };
          if (this.remember_me) {
            localStorage.setItem('user_info', JSON.stringify(user_info));
            localStorage.setItem('token', res.data.token);
            sessionStorage.removeItem('token');
            sessionStorage.removeItem('user_info');
          } else {
            sessionStorage.setItem('token', res.data.token);
            sessionStorage.setItem('user_info', JSON.stringify(user_info));
            localStorage.removeItem('token');
            localStorage.removeItem('user_info');
          }
          this.$message({
            message: '登录成功',
            type: 'success'
          });
          this.$router.push('/home');
        }
      },
      login_fail(error, message) {
        this.$message({
          message: message,
          type: 'error'
        });
        localStorage.removeItem('user_info');
      },
      user_login() {
        this.$axios({
          url: this.$settings.HOST + 'user/login/',
          method: 'post',
          data: {
            username: this.account,
            password: this.pwd
          }
        }).then(res => {
          this.login_success(res);
        }).catch(error => {
          this.login_fail(error, '用户名或密码错误');
          console.log(error);
        });
      },
      check_info() {  // 检查是否已保存密码，若保存则自动填写
        let user_info = JSON.parse(localStorage.getItem('user_info'));
        if (user_info) {
          this.account = user_info.account;
          this.pwd = user_info.pwd;
          this.remember_me = true;
        }
      },
      get_code() {
        if (!/1[356789]\d{9}/.test(this.phone)) {
          this.$message({message: '手机号格式有误', type: 'warning', showClose: true});
          return false
        }
        this.sms_btn = `正在发送`;
        this.is_send = true;
        this.$axios.get(this.$settings.HOST + `user/sms/${this.phone}/`).then(res => {
          if (res.status === 200) {
            this.$message({message: '发送成功', type: 'success', showClose: true});
            this.countdown();
          }
        }).catch(error => {
          console.log(error.response);
          this.$message.error(error.response.data.message);
          this.sms_btn = `获取验证码`;
          this.is_send = false;
        });
      },
      countdown() {
        this.is_send = true;
        let interval = 60;
        let timer = setInterval(() => {
          if (interval <= 0) {
            // 停止倒计时  允许发送短信
            this.is_send = false; // 设置允许发送短信 false
            this.sms_btn = `获取验证码`;
            clearInterval(timer);
          } else {
            interval--;
            this.sms_btn = `${interval}s后可以重新发送`;
          }
        }, 1000);
      },
      login_by_phone() {
        if (this.phone && this.code) {
          this.is_sub = true;
          this.login_btn = '请稍候';
          // 发起登录请求
          this.$axios({
            url: this.$settings.HOST + 'user/login_by_phone/',
            method: 'post',
            data: {
              phone: this.phone,
              code: this.code,
              login: 1
            }
          }).then(res => {
            this.is_sub = false;
            this.login_btn = '登录';
            this.login_success(res)
          }).catch(error => {
            this.is_sub = false;
            this.login_btn = '登录';
            this.login_fail(error, '验证码有误或已过期');
            console.log(error.response);
          });
        } else {
          this.$message({message: '手机号和验证码不能为空', type: 'warning', showClose: true});
        }
      }
    },
    created() {
      this.check_info();
    }
  }
</script>

<style scoped>
  .box {
    width: 100%;
    height: 100%;
    position: relative;
    overflow: hidden;
  }

  .box img {
    width: 100%;
    min-height: 100%;
  }

  .box .login {
    position: absolute;
    width: 500px;
    height: 400px;
    top: 0;
    left: 0;
    margin: auto;
    right: 0;
    bottom: 0;
    top: -338px;
  }

  .login .login-title {
    width: 100%;
    text-align: center;
  }

  .login-title img {
    width: 190px;
    height: auto;
  }

  .login-title p {
    font-family: PingFangSC-Regular;
    font-size: 18px;
    color: #fff;
    letter-spacing: .29px;
    padding-top: 10px;
    padding-bottom: 50px;
  }

  .login_box {
    width: 400px;
    height: auto;
    background: #fff;
    box-shadow: 0 2px 4px 0 rgba(0, 0, 0, .5);
    border-radius: 4px;
    margin: 0 auto;
    padding-bottom: 40px;
  }

  .login_box .title {
    font-size: 20px;
    color: #9b9b9b;
    letter-spacing: .32px;
    border-bottom: 1px solid #e6e6e6;
    display: flex;
    justify-content: space-around;
    padding: 50px 60px 0 60px;
    margin-bottom: 20px;
    cursor: pointer;
  }

  .login_box .title .selected {
    color: #4a4a4a;
    border-bottom: 2px solid #84cc39;
  }

  .inp {
    width: 350px;
    margin: 0 auto;
  }

  .inp input {
    border: 0;
    outline: 0;
    width: 100%;
    height: 45px;
    border-radius: 4px;
    border: 1px solid #d9d9d9;
    text-indent: 20px;
    font-size: 14px;
    background: #fff !important;
  }

  .inp input.user {
    margin-bottom: 16px;
  }

  .inp .rember {
    display: flex;
    justify-content: space-between;
    align-items: center;
    position: relative;
    margin-top: 10px;
  }

  .inp .rember p:first-of-type {
    font-size: 12px;
    color: #4a4a4a;
    letter-spacing: .19px;
    margin-left: 22px;
    display: -ms-flexbox;
    display: flex;
    -ms-flex-align: center;
    align-items: center;
    /*position: relative;*/
  }

  .inp .rember p:nth-of-type(2) {
    font-size: 14px;
    color: #9b9b9b;
    letter-spacing: .19px;
    cursor: pointer;
  }

  .inp .rember input {
    outline: 0;
    width: 30px;
    height: 45px;
    border-radius: 4px;
    border: 1px solid #d9d9d9;
    text-indent: 20px;
    font-size: 14px;
    background: #fff !important;
  }

  .inp .rember p span {
    display: inline-block;
    font-size: 12px;
    width: 100px;
    /*position: absolute;*/
    /*left: 20px;*/

  }

  #geetest {
    margin-top: 20px;
  }

  .login_btn {
    width: 100%;
    height: 45px;
    background: #84cc39;
    border-radius: 5px;
    font-size: 16px;
    color: #fff;
    letter-spacing: .26px;
    margin-top: 30px;
  }

  .inp .go_login {
    text-align: center;
    font-size: 14px;
    color: #9b9b9b;
    letter-spacing: .26px;
    padding-top: 20px;
  }

  .inp .go_login span {
    color: #84cc39;
    cursor: pointer;
  }
</style>
