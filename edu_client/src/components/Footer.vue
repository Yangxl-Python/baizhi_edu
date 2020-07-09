<template>
  <div class="footer">
    <ul>
      <li v-for="(nav,index) in nav_list" :key="index" v-if="nav.position === 2">
        <span>
          <a :href="nav.link">{{nav.title}}</a>
        </span>
      </li>
    </ul>
  </div>
</template>

<script>
  export default {
    name: "Footer",
    props: ['nav_list'],
  }
</script>

<style scoped>
  .footer {
    width: 100%;
    height: 128px;
    background: #25292e;
    color: #fff;
  }

  .footer ul {
    margin: 0 auto 16px;
    padding-top: 38px;
    width: 810px;
  }

  .footer ul li {
    float: left;
    width: 112px;
    margin: 0 10px;
    text-align: center;
    font-size: 14px;
  }

  .footer ul::after {
    content: "";
    display: block;
    clear: both;
  }

  .footer p {
    text-align: center;
    font-size: 12px;
  }

  .footer ul li span a {
    color: white;
  }

</style>
