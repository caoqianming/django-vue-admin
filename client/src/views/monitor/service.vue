
  <template>
  <div class="app-container">
  
<div class="box-card">
<el-row :gutter="12">
  <el-col :span="8">
    <el-card shadow="always">
      
      <div slot="header" class="clearfix">
    <span>CPU</span>
     </div>
     <el-row class="row">
        <el-col :span="8">
          属性
        </el-col>
         <el-col :span="8">
           值
        </el-col>
     </el-row>
      <el-row class="rowlist">
        <el-col :span="8">
          逻辑核心数
        </el-col>
         <el-col :span="8">
          {{cpuData.count}}
        </el-col>
     </el-row>
      <el-row class="rowlist">
        <el-col :span="8">
          物理核心数
        </el-col>
         <el-col :span="8">
         {{cpuData.lcount}}
        </el-col>
     </el-row>
      <el-row class="rowlist">
        <el-col :span="8">
          当前使用率
        </el-col>
         <el-col :span="8">
           {{cpuData.percent}}%
        </el-col>
     </el-row>
   
    </el-card>
  </el-col>
  <el-col :span="8">
    <el-card shadow="always">
      
      <div slot="header" class="clearfix">
    <span>内存</span>
     </div>
       <el-row class="row">
        <el-col :span="8">
          属性
        </el-col>
         <el-col :span="8">
           值
        </el-col>
     </el-row>
      <el-row class="rowlist">
        <el-col :span="8">
          使用率
        </el-col>
         <el-col :span="8">
          {{memoryData.percent}}%
        </el-col>
     </el-row>
      <el-row class="rowlist">
        <el-col :span="8">
          总内存
        </el-col>
         <el-col :span="8">
         {{memoryData.total}}
        </el-col>
     </el-row>
      <el-row class="rowlist">
        <el-col :span="8">
          已用内存
        </el-col>
         <el-col :span="8">
           {{memoryData.used}}
        </el-col>
     </el-row>
    
    </el-card>
  </el-col>
  <el-col :span="8">
    <el-card shadow="always">
      
      <div slot="header" class="clearfix">
    <span>硬盘</span>
     </div>
       <el-row class="row">
        <el-col :span="8">
          属性
        </el-col>
         <el-col :span="8">
           值
        </el-col>
     </el-row>
      <el-row class="rowlist">
        <el-col :span="8">
          已用百分比
        </el-col>
         <el-col :span="8">
          {{diskData.percent}}%
        </el-col>
     </el-row>
      <el-row class="rowlist">
        <el-col :span="8">
          总大小
        </el-col>
         <el-col :span="8">
         {{diskData.total}}
        </el-col>
     </el-row>
      <el-row class="rowlist">
        <el-col :span="8">
          已用大小
        </el-col>
         <el-col :span="8">
           {{diskData.used}}
        </el-col>
     </el-row>
    
   

    </el-card>
  </el-col>
</el-row>

</div>

<el-card class="box-card">
  <div slot="header" class="clearfix">
    <span>日志列表</span>
     </div>
 <div>
      <el-input
              v-model="listQuery.name"
              placeholder="日志名称"
              style="width: 300px"
              class="filter-item"
              @keyup.enter.native="handleFilter"
            />
            <el-button
              class="filter-item"
              type="primary"
              icon="el-icon-search"
              @click="handleFilter"
              >搜索</el-button
            >
            <el-button
              class="filter-item"
              type="primary"
              icon="el-icon-refresh-left"
              @click="resetFilter"
              >重置</el-button
            >
    </div>
    <el-table
      :data="tableData"
      style="width: 100%;height:400px">
      <el-table-column
        prop="name"
        label="日志名称"
        >
      </el-table-column>
      <el-table-column
        prop="size"
        label="日志大小"
        >
      </el-table-column>
      <el-table-column
      fixed="right"
      label="操作"
      width="100">
      <template slot-scope="scope">
        <el-button @click="handleClick(scope.row)" type="text" size="small">查看详情</el-button>
      </template>
    </el-table-column>
    </el-table>
<el-dialog
 
  :visible.sync="dialogVisible"
  width="80%"
  height:300px
  >

   
   <div v-html="logdec"> </div>
  

</el-dialog>
</el-card>
</div>

  </template>


<script>
import {getlogList,getLog,getServerList} from "@/api/moritor";
const defaultCMA = {
 
}
export default {
  components: {  },
  data() {
    return {
      tableData:[],
      cpuData:[],
      diskData:[],
      memoryData:[],
      dialogVisible: false,
      logdec:"",
      text:"",
      listQuery: {},
    };
  },
  computed: {},
  watch: {},
  created() {
    this.getlogList();
    this.getServerList();
  },
  methods: {
    
     getlogList() {
      getlogList(this.listQuery).then((response) => {
        if(response.data) {
        
          this.tableData=response.data;
        }
        
      });
    },
   handleFilter() {
      this.getlogList();
    },
    resetFilter() {
     
      this.getlogList();
    },
     getServerList() {
      getServerList().then((response) => {
        if (response.data) {
          this.cpuData = response.data.cpu;
          this.diskData = response.data.disk;
          this.memoryData = response.data.memory;
        }
        
      });
    },
   handleClick(row){
     this.dialogVisible = true;
     getLog(row.name).then((response) => {
        if (response.data) {
         this.logdec=response.data.replace(/\n/gm,"<br/>")
        
        }
        
      });

   },
  },
};
</script>
<style>
  .text {
    font-size: 14px;
  }

  .item {
    margin-bottom: 18px;
  }

  .clearfix:before,
  .clearfix:after {
    display: table;
    content: "";
  }
  .clearfix:after {
    clear: both
  }

  .box-card {
    width: 90%;
    margin:0 auto;
    margin-top:30px;
  }
  .row{border-bottom: 1px solid #dfe6ec;color: #909399;font-weight: 500;padding: 10px;}
  .rowlist{
    border-bottom: 1px solid #dfe6ec;color:#606266;font-weight: 500;padding: 10px;
  }
</style>
