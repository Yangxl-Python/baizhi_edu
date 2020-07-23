<template>
  <div class="user-order">
    <div class="main">
      <div class="banner"></div>
      <div class="profile">
        <div class="profile-info">
          <div class="avatar"><img class="newImg" width="100%" alt="" src="../../../static/image/user.png"></div>
          <span class="user-name">{{username}}</span>
          <span class="user-job">北京市 | Python</span>
        </div>
        <ul class="my-item">
          <li>我的账户</li>
          <li class="active">我的订单</li>
          <li>个人资料</li>
          <li>账号安全</li>
        </ul>
      </div>
      <div class="user-data">
        <ul class="nav">
          <li class="order-info">订单</li>
          <li class="course-expire">有效期</li>
          <li class="course-price">课程价格</li>
          <li class="real-price">实付金额</li>
          <li class="order-status">交易状态</li>
          <li class="order-do">交易操作</li>
        </ul>
        <div class="my-order-item" v-for="order in order_list" :key="order.order_number">
          <div class="user-data-header">
            <span class="order-time">{{order.create_time.replace(/T/g,' ').replace(/\.[\d]{6}/,'')}}</span>
            <span class="order-num">订单号：
                        <span class="my-older-number">{{order.order_number}}</span>
                    </span>
          </div>
          <ul class="nav user-data-list" v-for="detail in order.order_detail_list" :key="detail.id">
            <li class="order-info">
              <img :src="detail.course_img" alt="">
              <div class="order-info-title">
                <p class="course-title">{{detail.course_name}}</p>
                <p class="price-service" v-if="detail.discount_name">{{detail.discount_name}}</p>
              </div>
            </li>
            <li class="course-expire" v-if="detail.expire === 0">永久有效</li>
            <li class="course-expire" v-else>{{detail.expire}}天</li>
            <li class="course-price">{{detail.price.toFixed(2)}}</li>
            <li class="real-price">{{detail.real_price.toFixed(2)}}</li>
            <li class="order-status">{{order.order_status_name}}</li>
            <li class="order-do">
              <span class="btn btn2" v-if="order.order_status_name === '未支付'"
                    @click="go_pay(order.order_number)">去支付</span>
              <span class="btn btn2" v-else-if="order.order_status_name === '已支付'">去学习</span>
              <span class="btn btn2" v-else>重新下单</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
  export default {
    name: "OrderList",
    data() {
      return {
        token: '',
        username: '',
        order_list: [{
          'create_time': '',
          'order_detail_list': [],
          'order_status_name': ''
        }],
      }
    },
    methods: {
      get_data(data) {
        return localStorage.getItem(data) || sessionStorage.getItem(data);
      },
      get_token() {
        this.token = this.get_data('token');
      },
      get_username() {
        let user_info = JSON.parse(this.get_data('user_info'));
        this.username = user_info.username;
      },
      get_order_list() {
        this.$axios({
          url: `${this.$settings.HOST}order/list/`,
          headers: {
            Authorization: `jwt ${this.token}`
          },
          method: 'get'
        }).then(res => {
          this.order_list = res.data;
        }).catch(err => {
          if (err.response.status === 401) {
            this.$alert('登录已过期，请重新登录', '提示', {
              confirmButtonText: '确定',
              callback: action => {
                if (action === 'confirm') {
                  this.$router.push('/login');
                } else {
                  this.$router.push('/');
                }
              }
            });
          }
          console.log(err);
        });
      },
      go_pay(order_number) {
        this.$axios({
          url: `${this.$settings.HOST}payments/alipay/`,
          method: 'get',
          params: {
            order_number: order_number
          },
          headers: {
            Authorization: `jwt ${this.token}`
          }
        }).then(res => {
          location.href = res.data;
        }).catch(err => {
          console.log(err.response);
        });
      }
    },
    created() {
      this.get_token();
      this.get_username();
      this.get_order_list();
    }
  }
</script>

<style scoped>
  .main .banner {
    width: 100%;
    height: 324px;
    background: url(../../../static/image/5c8877290ad55.png) no-repeat;
    background-size: cover;
    z-index: 1;
  }

  .profile {
    width: 1200px;
    margin: 0 auto;
  }

  .profile-info {
    text-align: center;
    margin-top: -80px;
  }

  .avatar {
    width: 120px;
    height: 120px;
    border-radius: 60px;
    overflow: hidden;
    margin: 0 auto;
  }

  .user-name {
    display: block;
    font-size: 24px;
    color: #4a4a4a;
    margin-top: 14px;
  }

  .user-job {
    display: block;
    font-size: 11px;
    color: #9b9b9b;
  }

  .my-item {
    list-style: none;
    line-height: 1.42857143;
    color: #333;
    width: 474px;
    height: 31px;
    display: -ms-flexbox;
    display: flex;
    cursor: pointer;
    margin: 41px auto 0;
    -ms-flex-pack: justify;
    justify-content: space-between;
  }

  .my-item .active {
    border-bottom: 1px solid #000;
  }

  .user-data {
    width: 1200px;
    height: auto;
    margin: 0 auto;
    padding-top: 30px;
    border-top: 1px solid #e8e8e8;
    margin-bottom: 63px;
  }

  .nav {
    width: 100%;
    height: 60px;
    background: #e9e9e9;
    display: -ms-flexbox;
    display: flex;
    -ms-flex-align: center;
    align-items: center;
  }

  .nav li {
    margin-left: 20px;
    margin-right: 28px;
    height: 60px;
    line-height: 60px;
    list-style: none;
    font-size: 13px;
    color: #333;
    border-bottom: 1px solid #e9e9e9;
    width: 160px;
  }

  .nav .order-info {
    width: 325px;
  }

  .nav .course-expire {
    width: 60px;
  }

  .nav .course-price {
    width: 130px;
  }

  .user-data-header {
    display: flex;
    height: 44px;
    color: #4a4a4a;
    font-size: 14px;
    background: #f3f3f3;
    -ms-flex-align: center;
    align-items: center;
  }

  .order-time {
    font-size: 12px;
    display: inline-block;
    margin-left: 20px;
  }

  .order-num {
    font-size: 12px;
    display: inline-block;
    margin-left: 29px;
  }

  .user-data-list {
    height: 100%;
    display: flex;
  }

  .user-data-list {
    background: none;
  }

  .user-data-list li {
    height: 60px;
    line-height: 60px;
  }

  .user-data-list .order-info {
    display: flex;
    align-items: center;
    margin-right: 28px;
  }

  .user-data-list .order-info img {
    max-width: 100px;
    max-height: 75px;
    margin-right: 22px;
  }

  .course-title {
    width: 203px;
    font-size: 13px;
    color: #333;
    line-height: 20px;
    margin-top: -10px;
  }

  .order-info-title .price-service {
    line-height: 18px;
  }

  .price-service {
    font-size: 12px;
    color: #fa6240;
    padding: 0 5px;
    border: 1px solid #fa6240;
    border-radius: 4px;
    margin-top: 4px;
    position: absolute;
  }

  .order-info-title {
    margin-top: -10px;
  }

  .user-data-list .course-expire {
    font-size: 12px;
    color: #ff5502;
    width: 60px;
    text-align: center;
  }

  .btn {
    width: 100px;
    height: 32px;
    font-size: 14px;
    color: #fff;
    background: #ffc210;
    border-radius: 4px;
    border: none;
    outline: none;
    transition: all .25s ease;
    display: inline-block;
    line-height: 32px;
    text-align: center;
    cursor: pointer;
  }
</style>
