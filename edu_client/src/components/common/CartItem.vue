<template>
  <div class="cart_item">
    <div class="cart_column column_1">
      <el-checkbox class="my_el_checkbox" v-model="course.selected"/>
    </div>
    <div class="cart_column column_2">
      <img :src="course.course_img" alt="">
      <span><router-link :to="`/home/course/detail/${course.id}`">{{course.name}}</router-link></span>
    </div>
    <div class="cart_column column_3">
      <el-select v-model="course.expire_time" size="mini" placeholder="请选择有效期" class="my_el_select">
        <el-option :label="expire.expire_text" :value="expire.expire_time" :key="expire.id"
                   v-for="expire in course.expire_list"/>
      </el-select>
    </div>
    <div class="cart_column column_4">¥{{course.price.toFixed(2)}}</div>
    <div class="cart_column column_4" @click="delete_course">删除</div>
  </div>
</template>

<script>
  export default {
    name: "CartItem",
    props: ['course', 'checked'],
    watch: {
      'course.selected': function () {
        this.change_select();
      },
      'course.expire_time': function () {
        let token = this.get_token();
        this.$axios({
          url: `${this.$settings.HOST}cart/option/`,
          method: 'put',
          data: {
            course_id: this.course.id,
            expire_time: this.course.expire_time
          },
          headers: {
            Authorization: `jwt ${token}`
          }
        }).then(res => {
          this.$message.success(res.data.message);
          this.course.price = res.data.real_expire_price;
          this.$parent.get_cart();
        }).catch(err => {
          if (err.response.status === 400) {
            this.$message.error(err.response.data.message);
          } else {
            console.log(err.response);
          }
        });
      },
      'checked': function () {
        this.course.selected = this.checked;
      }
    },
    methods: {
      get_token() {
        return localStorage.getItem('token') || sessionStorage.getItem('token');
      },
      change_select() {
        let token = this.get_token();
        this.$axios({
          url: `${this.$settings.HOST}cart/option/`,
          method: 'patch',
          data: {
            selected: this.course.selected,
            course_id: this.course.id
          },
          headers: {
            Authorization: `jwt ${token}`
          }
        }).then(res => {
          this.$message.success(res.data.message);
          this.$parent.change_status();
          this.$parent.compute_total_price();
        }).catch(err => {
          console.log(err.response);
        });
      },
      delete_course() {
        let token = this.get_token();
        this.$axios({
          url: `${this.$settings.HOST}cart/option/`,
          method: 'delete',
          data: {
            course_id: this.course.id
          },
          headers: {
            Authorization: `jwt ${token}`
          }
        }).then(res => {
          this.$message.success(res.data.message);
          this.$parent.get_cart();
        }).catch(err => {
          console.log(err.response);
        });
      }
    }
  }
</script>

<style scoped>
  .cart_item::after {
    content: "";
    display: block;
    clear: both;
  }

  .cart_column {
    float: left;
    height: 250px;
  }

  .cart_item .column_1 {
    width: 88px;
    position: relative;
  }

  .my_el_checkbox {
    position: absolute;
    left: 0;
    right: 0;
    bottom: 0;
    top: 0;
    margin: auto;
    width: 16px;
    height: 16px;
  }

  .cart_item .column_2 {
    padding: 67px 10px;
    width: 520px;
    height: 116px;
  }

  .cart_item .column_2 img {
    width: 175px;
    height: 115px;
    margin-right: 35px;
    vertical-align: middle;
  }

  .cart_item .column_3 {
    width: 197px;
    position: relative;
    padding-left: 10px;
  }

  .my_el_select {
    width: 117px;
    height: 28px;
    position: absolute;
    top: 0;
    bottom: 0;
    margin: auto;
  }

  .cart_item .column_4 {
    padding: 67px 10px;
    height: 116px;
    width: 142px;
    line-height: 116px;
  }

</style>
