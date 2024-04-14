<template>
  <div class="app-container">
    <el-card style="margin-bottom: 10px">
      <div>
        <el-select v-model="filter.workflow" placeholder="工作流" clearable style="width: 200px" class="filter-item" @change="handleFilter">
          <el-option
            v-for="item in workFlows"
            :key="item.id"
            :label="item.name"
            :value="item.id"
          />
        </el-select>
        <el-select v-model="filter.act_state" placeholder="工单进行状态" clearable style="width: 200px" class="filter-item" @change="handleFilter">
          <el-option label="草稿中" value="0" />
          <el-option label="进行中" value="1" />
          <el-option label="被退回" value="2" />
          <el-option label="被撤回" value="3" />
          <el-option label="已完成" value="4" />
          <el-option label="已关闭" value="5" />
        </el-select>
        <el-button
          class="filter-item"
          type="primary"
          icon="el-icon-refresh-left"
          @click="resetFilter"
        >重置</el-button>
        <el-button
          class="filter-item"
          type="primary"
          icon="el-icon-search"
          @click="handleFilter"
        >搜索</el-button>
      </div>
    </el-card>
    <el-card>
      <el-table :data="tickets"
                border fit stripe
                style="width: 100%"
                height="100"
                highlight-current-row
                v-el-height-adaptive-table="{bottomOffset: 60}">
        <el-table-column label="工单标题" min-width="100" prop="title">
        </el-table-column>
        <el-table-column label="当前状态"  min-width="100">
          <template slot-scope="scope">
            <el-tag v-if="scope.row.act_state==0" label="草稿中" value="scope.row.act_state">草稿中</el-tag>
            <el-tag v-else-if="scope.row.act_state==1" label="进行中" value="scope.row.act_state">进行中</el-tag>
            <el-tag v-else-if="scope.row.act_state==2" label="被退回" value="scope.row.act_state">被退回</el-tag>
            <el-tag v-else-if="scope.row.act_state==3" label="被撤回" value="scope.row.act_state">被撤回</el-tag>
            <el-tag v-else-if="scope.row.act_state==4" label="已完成" value="scope.row.act_state">已完成</el-tag>
            <el-tag v-else-if="scope.row.act_state==5" label="已关闭" value="scope.row.act_state">已关闭</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="进行状态"  min-width="100">
          <template slot-scope="scope">
            <span v-if="scope.row.state_.type==0">{{scope.row.state_.name}}中</span>
            <span v-else>已{{scope.row.state_.name}}</span>
          </template>
        </el-table-column>
        <el-table-column label="类型"  min-width="100">
          <template slot-scope="scope">{{ scope.row.workflow_.name }}</template>
        </el-table-column>
        <el-table-column label="创建时间"  min-width="100" prop="create_time">
        </el-table-column>
        <el-table-column align="center" label="操作">
          <template slot-scope="scope">
            <el-link type="success" @click="handleLogs(scope)">工单日志</el-link>
          </template>
        </el-table-column>
      </el-table>
      <pagination
        :total="total"
        :page.sync="filter.page"
        :limit.sync="filter.page_size"
        @pagination="getList"
      />
    </el-card>
    <el-dialog :visible.sync="limitedFlowLogs" title="工单日志">
      <el-table :data="floeLogs"  fit stripe
                style="width: 100%;border-top:1px solid #EBEEF5;"
                height="100"
                highlight-current-row
                v-el-height-adaptive-table="{bottomOffset: 60}">
        <el-table-column label="工单标题" min-width="100">
          <template slot-scope="scope" v-if="scope.row.ticket_data">
            <span>{{scope.row.ticket_data.title}}中</span>
          </template>
        </el-table-column>
       <!-- <el-table-column label="当前状态"  min-width="100">
          <template slot-scope="scope">
            <el-tag v-if="scope.row.act_state==0" label="草稿中" value="scope.row.act_state">草稿中</el-tag>
            <el-tag v-else-if="scope.row.act_state==1" label="进行中" value="scope.row.act_state">进行中</el-tag>
            <el-tag v-else-if="scope.row.act_state==2" label="被退回" value="scope.row.act_state">被退回</el-tag>
            <el-tag v-else-if="scope.row.act_state==3" label="被撤回" value="scope.row.act_state">被撤回</el-tag>
            <el-tag v-else-if="scope.row.act_state==4" label="已完成" value="scope.row.act_state">已完成</el-tag>
            <el-tag v-else-if="scope.row.act_state==5" label="已关闭" value="scope.row.act_state">已关闭</el-tag>
          </template>
        </el-table-column>-->
        <el-table-column label="进行状态"  min-width="100">
          <template slot-scope="scope" v-if="scope.row.state_">
            <span v-if="scope.row.state_.type==0">{{scope.row.state_.name}}中</span>
            <span v-else>已{{scope.row.state_.name}}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作人"  min-width="100">
          <template slot-scope="scope" v-if="scope.row.participant_">{{ scope.row.participant_.name }}</template>
        </el-table-column>
        <el-table-column label="操作意见" min-width="100" prop="suggestion">
        </el-table-column>
        <el-table-column label="更新时间"  min-width="100" prop="update_time">
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>
<script>
  import {getWorkflowList,getTickets,getTicketFlowlog} from "@/api/workflow";
  import Pagination from "@/components/Pagination";
  export default {
  name: "workFlowTickets",
  components: { Pagination },
    inject:['reload'],
  data(){
    return{
      sort:0,
      total:0,
      filter:{
        page:1,
        page_size:20,
        state:'',
        act_state:'',
        workflow:'',
        category:'all',
        search:'',
      },
      listLoading:false,
      limitedFlowLogs:false,
      floeLogs:[],
      tickets:[],
      workFlows:[],
    }
  },
    mounted(){
      this.workflow = this.$route.params.workflow;
      if(this.workflow){//有传参
        this.filter.workflow = parseInt(this.workflow);
      }
      this.getList();
      this.getWorkFlow();
    },
  methods:{
    getList(){
      this.listLoading = true;
      getTickets( this.filter).then((res)=>{
        if(res.data.results){
          this.total = res.data.count;
          this.tickets = res.data.results;
          this.listLoading = false;
        }
      })
    },
    //获取工作流
    getWorkFlow(){
      let listForm = {page:0};
      getWorkflowList(listForm).then((response) => {
        if (response.data) {
          this.workFlows = response.data;
        }
      });
    },
    //查询搜索
    handleFilter(){
      this.filter.page=1;
      this.getList();
    },
    //筛选重置
    resetFilter(){
      this.filter.workflow = '';
      this.filter.act_state = '';
        this.getList();
    },
    handleLogs(scope){
      let id = scope.row.id;
      this.limitedFlowLogs = true;
      getTicketFlowlog(id).then(res=>{
        if(res.data){
          this.floeLogs = res.data;
        }
      })
    },
  }
  }
</script>

<style scoped>

</style>
