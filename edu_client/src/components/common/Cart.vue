<template>
  <div class="cart">
    <div class="cart_info">
      <div class="cart_title">
        <span class="text">我的购物车</span>
        <span class="total">共4门课程</span>
      </div>
      <div class="cart_table">
        <div class="cart_head_row">
          <span class="doing_row"></span>
          <span class="course_row">课程</span>
          <span class="expire_row">有效期</span>
          <span class="price_row">单价</span>
          <span class="do_more">操作</span>
        </div>
        <div class="cart_course_list">
          <CartItem v-for="cart in cart_list" :key="cart.id" :course="cart" :checked="change_all"/>
        </div>
        <div class="cart_footer_row">
          <span class="cart_select">
            <label>
              <el-checkbox v-model="checked" @change="select_all" :indeterminate="isIndeterminate"/>
              <span>全选</span>
            </label>
          </span>
          <span class="cart_delete"><i class="el-icon-delete"/> <span>删除</span></span>
          <router-link to="/home/order"><span class="goto_pay">去结算</span></router-link>
          <span class="cart_total">总计：¥{{total_price.toFixed(2)}}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
  import CartItem from "./CartItem";

  export default {
    name: "Cart",
    components: {
      CartItem: CartItem
    },
    data() {
      return {
        cart_list: [],
        checked: false,
        change_all: false,
        total_price: 0,
        isIndeterminate: false
      }
    },
    methods: {
      check_user() {
        // 检查是否登录
        let token = localStorage.getItem('token') || sessionStorage.getItem('token');
        if (!token) {
          this.$router.push('/login');
          return false;
        }
        return token;
      },
      get_cart() {
        let token = this.check_user();
        this.$axios.get(`${this.$settings.HOST}cart/option/`, {
          headers: {
            Authorization: `jwt ${token}`
          }
        }).then(res => {
          this.$store.commit('add_cart', res.data.cart_list.length);
          this.cart_list = res.data.cart_list;
          this.total_price = res.data.total_price;
          this.change_status();
          this.select_all();
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
          } else {
            console.log(err.response);
          }
        });
      },
      select_all() {
        this.change_all = this.checked;
      },
      change_status() {
        let cart_list_length = this.cart_list.length;
        let checkedCount = 0;
        for (let i = 0; i < cart_list_length; i++) {
          if (this.cart_list[i].selected) {
            checkedCount += 1;
          }
        }
        if (checkedCount === cart_list_length) {
          this.isIndeterminate = false;
          this.checked = true;
        } else if (checkedCount === 0) {
          this.isIndeterminate = false;
          this.checked = false;
        } else {
          this.isIndeterminate = true;
          this.checked = false;
        }
      },
      compute_total_price() {
        let total_price = 0.0;
        for (let i = 0; i < this.cart_list.length; i++) {
          if (this.cart_list[i].selected) {
            total_price += this.cart_list[i].price
          }
        }
        this.total_price = total_price;
      }
    },
    created() {
      this.get_cart();
    }
  }
</script>

<style scoped>
  .cart_info {
    width: 1200px;
    margin: 0 auto 200px;
  }

  .cart_title {
    margin: 25px 0;
  }

  .cart_title .text {
    font-size: 18px;
    color: #666;
  }

  .cart_title .total {
    font-size: 12px;
    color: #d0d0d0;
  }

  .cart_table {
    width: 1170px;
  }

  .cart_table .cart_head_row {
    background: #F7F7F7;
    width: 100%;
    height: 80px;
    line-height: 80px;
    padding-right: 30px;
  }

  .cart_table .cart_head_row::after {
    content: "";
    display: block;
    clear: both;
  }

  .cart_table .cart_head_row .doing_row,
  .cart_table .cart_head_row .course_row,
  .cart_table .cart_head_row .expire_row,
  .cart_table .cart_head_row .price_row,
  .cart_table .cart_head_row .do_more {
    padding-left: 10px;
    height: 80px;
    float: left;
  }

  .cart_table .cart_head_row .doing_row {
    width: 78px;
  }

  .cart_table .cart_head_row .course_row {
    width: 530px;
  }

  .cart_table .cart_head_row .expire_row {
    width: 188px;
  }

  .cart_table .cart_head_row .price_row {
    width: 162px;
  }

  .cart_table .cart_head_row .do_more {
    width: 162px;
  }

  .cart_footer_row {
    padding-left: 30px;
    background: #F7F7F7;
    width: 100%;
    height: 80px;
    line-height: 80px;
  }

  .cart_footer_row .cart_select span {
    margin-left: -7px;
    font-size: 18px;
    color: #666;
  }

  .cart_footer_row .cart_delete {
    margin-left: 58px;
  }

  .cart_delete .el-icon-delete {
    font-size: 18px;
  }

  .cart_delete span {
    margin-left: 15px;
    cursor: pointer;
    font-size: 18px;
    color: #666;
  }

  .cart_total {
    float: right;
    margin-right: 62px;
    font-size: 18px;
    color: #666;
  }

  .goto_pay {
    float: right;
    width: 159px;
    height: 80px;
    outline: none;
    border: none;
    background: #ffc210;
    font-size: 18px;
    color: #fff;
    text-align: center;
    cursor: pointer;
  }
</style>
