<template>
  <div>
    <Header :nav_list="nav_list"/>
    <router-view/>
    <Footer :nav_list="nav_list"/>
  </div>
</template>

<script>
  import Banner from "./common/Banner";
  import Header from "./common/Header";
  import Footer from "./common/Footer";

  export default {
    name: "Home",
    components: {
      Header: Header,
      Footer: Footer
    },
    data() {
      return {
        nav_list: [],
      }
    },
    methods: {
      get_all_nav() {
        this.$axios.get(this.$settings.HOST + 'home/nav/').then(res => {
          this.nav_list = res.data;
        }).catch(error => {
          console.log(error);
        });
      },
    },
    created() {
      this.get_all_nav();
    }
  }
</script>

<style scoped>

</style>
