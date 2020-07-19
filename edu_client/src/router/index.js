import Vue from 'vue'
import Router from 'vue-router'
import Home from "../components/Home";
import Login from "../components/Login";
import Register from "../components/Register";
import Course from "../components/common/Course";
import Banner from "../components/common/Banner";
import Detail from "../components/common/Detail";
import Cart from "../components/common/Cart";
import Order from "../components/common/Order";

Vue.use(Router);

export default new Router({
  routes: [
    {
      path: '/',
      redirect: '/home'
    },
    {
      path: '/home',
      component: Home,
      children: [
        {
          path: '',
          component: Banner
        },
        {
          path: 'course',
          component: Course
        },
        {
          path: 'course/detail/:id',
          component: Detail
        },
        {
          path: 'cart',
          component: Cart
        },
        {
          path: 'order',
          component: Order
        },
      ]
    },
    {
      path: '/login',
      name: 'Login',
      component: Login
    },
    {
      path: '/register',
      name: 'Register',
      component: Register
    },
  ]
})
