<template>
  <el-tabs v-model="activeName" @tab-click="handleClick">
    <el-tab-pane label="自定义字段" name="first">
      
       <CTF :ID="ID"></CTF>
    </el-tab-pane>
    <el-tab-pane label="状态" name="second">
      
        <State :ID="ID"></State>
        
    </el-tab-pane>
    <el-tab-pane label="流转" name="third">
       <TST :ID="ID"></TST>
    </el-tab-pane>
  </el-tabs>
</template>
<script>
import State from "@/views/workflow/state"
import CTF from "@/views/workflow/customfield"
import TST from "@/views/workflow/transitions"
  export default {
     components: {State,CTF,TST},
    data() {
      return {
        activeName: 'first',
        ID:null
      };
    },
    created() {
      let id = sessionStorage.getItem('configurationId');
     if(this.$route.params.workflow){
       this.ID = this.$route.params.workflow;
       if(id){
         sessionStorage.removeItem('configurationId');
         sessionStorage.setItem('configurationId',this.$route.params.workflow);
       }else{
         sessionStorage.setItem('configurationId',this.$route.params.workflow);
       }
     }else{
       if(id){
         this.ID = id;
       }
     }
  },
    methods: {
      handleClick(tab, event) {
        console.log(tab, event);
      },
      
    }
  };
</script>
