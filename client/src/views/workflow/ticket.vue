<template>
  <div class="app-container">
    <el-card style="margin-bottom: 10px">
      <div>
        <el-select v-model="pageForm.workflow" placeholder="工作流" clearable style="width: 200px" class="filter-item" @change="handleFilter">
          <el-option
            v-for="item in workflows"
            :key="item.id"
            :label="item.name"
            :value="item.id"
          />
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
      <div style="margin-top: 2px">
        <el-button type="primary" icon="el-icon-plus" @click="handleCreate">新增</el-button>
      </div>
    </el-card>
    <el-tabs v-model="pageForm.category" type="border-card" @tab-click="handleClick">
      <el-tab-pane label="待处理" name="duty">
        <el-table
          v-loading="listLoading"
          :data="tickets"
          border fit stripe
          style="width: 100%"
          height="100"
          highlight-current-row
          v-el-height-adaptive-table="{bottomOffset: 100}"
        >
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
              <el-link v-if="scope.row.state_.distribute_type==1&&scope.row.participant_type==2" type="danger" @click="handleGetTicket(scope)">接单</el-link>
              <el-link v-else-if="(scope.row.act_state==1||scope.row.act_state==3)&&scope.row.participant_type!==2&&scope.row.state_.type===0" type="primary" @click="handleDetail(scope)">处理</el-link>
              <el-link v-if="scope.row.state_.type==1&&userId==1" type="danger" @click="handleClose(scope,'2')">关闭</el-link>
              <!--如果state_.retreat为可退回，则显示撤回按钮 state_.type==1处于草稿状态 -->
              <el-link v-if="scope.row.state_.enable_retreat&&userId==scope.row.create_by&&scope.row.state_.type!==1" type="danger" @click="handleClose(scope,'1')">撤回</el-link>
              <el-link  type="primary" @click="handleDetails(scope)">详情</el-link>
              <el-link type="success" @click="handleDelete(scope)">删除</el-link>
              <el-link type="success" @click="handlePicture(scope)">查看流程图</el-link>
              <el-link type="success" @click="handleLogs(scope)">工单日志</el-link>
            </template>
          </el-table-column>
        </el-table>
        <pagination
          :total="total"
          :page.sync="pageForm.page"
          :limit.sync="pageForm.page_size"
          @pagination="getList"
        />
      </el-tab-pane>
      <el-tab-pane label="我处理" name="worked">
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
             <!-- <el-link v-if="scope.row.state_.distribute_type==1&&scope.row.participant_type==2" type="danger" @click="handleGetTicket(scope)">接单</el-link>
              <el-link v-else-if="(scope.row.act_state==1||scope.row.act_state==3)&&scope.row.participant_type!==2&&scope.row.state_.type===0" type="primary" @click="handleDetail(scope)">处理</el-link>
              -->
              <el-link v-if="scope.row.state_.type==1&&userId==1" type="danger" @click="handleClose(scope,'2')">关闭</el-link>
              <el-link  type="primary" @click="handleDetails(scope)">详情</el-link>
              <el-link type="success" @click="handlePicture(scope)">查看流程图</el-link>
              <el-link type="success" @click="handleLogs(scope)">工单日志</el-link>
            </template>
          </el-table-column>
        </el-table>
        <pagination
          :total="total"
          :page.sync="pageForm.page"
          :limit.sync="pageForm.page_size"
          @pagination="getList"
        />
      </el-tab-pane>
      <el-tab-pane label="我发起" name="owner">
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
            <template slot-scope="scope" v-if="scope.row.state_">
              <el-link v-if="scope.row.state_.enable_retreat&&scope.row.state_.type!==1" type="danger" @click="handleClose(scope,'1')">撤回</el-link>
              <el-link v-if="scope.row.state_.type==1" type="danger" @click="handleClose(scope,'2')">关闭</el-link>
              <el-link  type="primary" @click="handleDetails(scope)">详情</el-link>
              <el-link type="success" @click="handleDelete(scope)">删除</el-link>
              <el-link type="success" @click="handlePicture(scope)">查看流程图</el-link>
              <el-link type="success" @click="handleLogs(scope)">工单日志</el-link>
            </template>
          </el-table-column>
        </el-table>
        <pagination
          :total="total"
          :page.sync="pageForm.page"
          :limit.sync="pageForm.page_size"
          @pagination="getList"
        />
      </el-tab-pane>
      <el-tab-pane label="抄送我" name="cc">
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
              <el-link  type="primary" @click="handleDetails(scope)">详情</el-link>
              <el-link type="danger" @click="handlePicture(scope)">查看流程图</el-link>
              <el-link type="success" @click="handleLogs(scope)">工单日志</el-link>
            </template>
          </el-table-column>
        </el-table>
        <pagination
          :total="total"
          :page.sync="pageForm.page"
          :limit.sync="pageForm.page_size"
          @pagination="getList"
        />
      </el-tab-pane>
    </el-tabs>
    <div class="svgMark" v-if="dialogVisible" @click="closeMark">
      <div class="svgWrapper">
        <div class="svgItem">工单流程图<i class="el-dialog__close el-icon el-icon-close" @click="closeMark"></i></div>
        <el-row>
          <el-col :span="12">
            <p>工单名称 ：{{watchedName}}</p>
          </el-col>
          <el-col :span="12">
            <p>创建时间 ：{{watchedCreateTime}}</p>
          </el-col>
        </el-row>
        <el-steps :active="actives" spac="400px" align-center="" style="padding-top: 20px;">
          <el-step :title="item.name" v-for="item in flowSteps " :key="item.id">
          </el-step>
        </el-steps>
        <div style="width: 90%;margin: auto;">
          <svg height=1000 id="mySvg" style="width:100%!important;">
          </svg>
        </div>

      </div>
    </div>
    <el-dialog :visible.sync="limitedRetreat" :title="handleTitle">
      <el-row>
        <el-form ref="Form" :model="handleForm" label-width="100px" label-position="right">
          <el-col :span="1" style="height: 1px;"></el-col>
          <el-col :span="22" style="margin:3vh 0">
            <el-form-item :label="handleLabel">
              <el-input type="textarea" :rows="3" v-model="handleForm.suggestion" placeholder="撤回原因"/>
            </el-form-item>
          </el-col>
        </el-form>
      </el-row>
      <div style="text-align: center">
        <el-button class="filter-item" type="" @click="handleCancel">取消</el-button>
        <el-button class="filter-item" type="primary" @click="handleSubmit">确定</el-button>
      </div>
    </el-dialog>
    <el-dialog :visible.sync="limitedAdd" title="新增工单">
      <el-form ref="Form" :model="addForm" label-width="100px" label-position="right" :rules="rule1">
        <el-form-item label="名称" prop="title">
          <el-input v-model="addForm.title" placeholder="工单名称" />
        </el-form-item>
        <el-form-item label="工作流">
          <el-select v-model="addForm.workflow" placeholder="工作流" @change="handleWorkflowChange">
            <el-option
              v-for="item in workflows"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item :label="item.field_name" v-for="item in customfields" :key="item.id">
          <template v-if="item.field_type=='string'">
            <el-input v-model="item.default_value" :placeholder="item.description" />
          </template>
          <template v-if="item.field_type==='int'">
            <el-input v-model="item.default_value" type="number" :placeholder="item.description" oninput="value=value.replace(/[^\d]/g,'')" />
          </template>
          <template v-if="item.field_type==='float'">
            <el-input v-model="item.default_value" type="number" :placeholder="item.description" />
          </template>
          <template v-if="item.field_type==='date'">
            <el-date-picker
              v-model="item.default_value"
              type="date"
              placeholder="选择日期"
              value-format="yyyy-MM-dd"
              style="width: 100%"
            >
            </el-date-picker>
          </template>
          <template v-if="item.field_type==='datetime'">
            <el-date-picker
              v-model="item.default_value"
              type="datetime"
              placeholder="选择日期"
              value-format="yyyy-MM-dd HH:mm:ss"
              style="width: 100%"
            >
            </el-date-picker>
          </template>
          <template v-if="item.field_type==='select'">
            <el-select style="width: 100%" v-model="item.default_value" placeholder="请选择">
              <el-option
                v-for="item1 in item.field_choice"
                :key="item1.id"
                :label="item1.name"
                :value="item1.id"
              >
              </el-option>
            </el-select>
          </template>
          <template v-if="item.field_type==='selects'">
            <el-select  style="width: 100%" multiple v-model="item.default_value" placeholder="请选择">
              <el-option
                v-for="item1 in item.field_choice"
                :key="item1.id"
                :label="item1.name"
                :value="item1.id"
              >
              </el-option>
            </el-select>
          </template>
          <template v-if="item.field_type==='textarea'">
            <el-input type="textarea"  :rows="3" v-model="item.default_value" placeholder="内容" />
          </template>
          <template v-if="item.field_type==='file'">
            <el-upload
              ref="upload"
              :action="upUrl"
              :on-preview="handlePreview"
              :on-success="handleUpSuccess"
              :on-remove="handleRemove"
              :headers="upHeaders"
              :file-list="fileList"
              :limit="1"
              accept=".doc,.docx,.xls,.xlsx,.ppt,.pptx"
            >
              <el-button size="small" type="primary">上传文件</el-button>
            </el-upload>
          </template>
        </el-form-item>
      </el-form>
      <div style="text-align: right">
        <el-button type="danger" @click="limitedAdd = false">取消</el-button>
        <el-button type="primary" @click="confirm('Form')">确认</el-button>
      </div>
    </el-dialog>
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
<script src="https://d3js.org/d3.v4.min.js"></script>
<script>
  import { upUrl, upHeaders } from "@/api/file";
  import {getWorkflowList,getWfCustomfieldList,createTicket,getWfStateList,getTickets,ticketAccpet,getWfTransitionList,
    ticketHandle,getWfFlowSteps,getTicketDetail,getTicketTransitions,getTicketFlowlog,ticketRetreat,ticketClose,ticketDestory} from "@/api/workflow";
  import Pagination from "@/components/Pagination";
  import dagreD3 from 'dagre-d3'
  import * as d3 from 'd3'
  export default {
  name: "ticket",
  components: { Pagination },
    inject:['reload'],
  data(){
    return{
      step:4,
      sort:0,
      total:0,
      actives:4,
      ticketId:0,
      pageForm:{
        page:1,
        page_size:20,
        workflow:'',
        category:'duty',
      },
      addForm:{
        title:'',
        workflow:'',
        ticket_data:{},
        transition:''
      },
      handleForm:{
        suggestion:'',
      },
      handleRule:{},
      upUrl: upUrl(),
      upHeaders: upHeaders(),
      keyword:'',
      workflow:'',
      watchedName:'',
      watchedCreateTime:'',
      logs:[],
      tickets:[],
      workflows:[],
      ticketDetail:{},
      dialogVisible:false,
      listLoading:false,
      limitedStep:false,
      limitedAdd:false,
      limitedRetreat:false,
      limitedFlowLogs:false,
      floeLogs:[],
      nodes: [],
      tooltip:null,
      edges: [],
      fileList:[],
      flowSteps:[],
      operationBtn:[],
      customfields:[],
      transitions:[],
      handleLabel:'撤回原因',
      handleTitle:'工单撤回',
      rule1:{
        title: [{ required: true, message: "请输入", trigger: "blur" }],
        workflow: [{ required: true, message: "选择", trigger: "blur" }]
      }
      ,
    }
  },
    mounted(){
    debugger;
    this.userId = sessionStorage.getItem('userId')
      this.workflow = this.$route.params.workflow;
      if(this.workflow){//有传参
        this.pageForm.workflow = parseInt(this.workflow);
      }
      this.getList();
      this.getStates();
      this.getWorkFlow();
    },
  methods:{
    getList(){
      this.listLoading = true;
      getTickets( this.pageForm).then((res)=>{
        if(res.data.results){
          this.total = res.data.count;
          this.tickets = res.data.results;
          this.listLoading = false;
        }
      })
    },
    getTicketFlowlogs(id){
      getTicketFlowlog(id).then(res=>{
        if(res.data){
          this.logs = res.data;
        }
      })
    },
    handleClick(tab, event) {
      console.log(tab, event);
      this.getList();
    },
    //获取工作流所有状态
    getStates(){
      if(this.pageForm.workflow!==''){
        getWfStateList(this.pageForm.workflow).then((response) => {
          if (response.data) {
            let nodes = [];
            let res = response.data;
            for(let i=0;i<res.length;i++){
              let obj = new Object();
              obj.id = res[i].id;
              obj.label = res[i].name;
              obj.shape = res[i].type===0? 'diamond':'rect';
              nodes.push(obj)
            }
            this.nodes = nodes;
            this.getEdges(nodes);
          }
        });
      }
    },
    //获取工作流
    getWorkFlow(){
      let listForm = {page:0};
      getWorkflowList(listForm).then((response) => {
        if (response.data) {
          this.workflows = response.data;
        }
      });
    },
    //获取过程标记
    getEdges(nodes){
        let edge = [];
        for(let i=1;i<nodes.length;i++){
          let obj = new Object();
          obj.source = nodes[i-1].id;
          obj.target = nodes[i].id;
          obj.label = i>1?'同意':'';
          edge.push(obj);
        }
        this.edges = edge;
    },
    handleFilter(){
      this.pageForm.page=1;
      this.getList();
      this.getStates();
    },
    resetFilter(){
      this.pageForm.workflow = '',
        this.getList();
    },
    handleCreate(){
      this.limitedAdd = true;
      this.addForm.title = '';
      this.addForm.workflow = '';
      this.addForm.ticket_data = {};
      this.addForm.transition = '';
      this.customfields = [];
      this.$nextTick(() => {
        this.$refs["Form"].clearValidate();
      });
    },
    handleWorkflowChange(){
      //获取字段
      getWfCustomfieldList(this.addForm.workflow).then((res)=>{
        this.customfields = res.data;
      })
      //获取流转
      getWfTransitionList(this.addForm.workflow).then((res)=>{
        for (let i=0;i<res.data.length;i++){
          if(res.data[i].source_state_.type ===1){
            debugger;
            this.addForm.transition = res.data[i].id;
          }
        }
      })
    },
    handlePreview(file) {
      if ("url" in file) {
        window.open(file.url);
      } else {
        window.open(file.response.data.path);
      }
    },
    handleUpSuccess(res, file, filelist) {
      this.process.instruction = res.data.id;
    },
    handleRemove(file, filelist){
      this.process.instruction = null;
    },
    confirm(form){
      this.$refs[form].validate((valid) => {
        if (valid) {
          let fields = this.customfields;
          let obj = new Object();
          for(let i=0;i<fields.length;i++){
            obj[fields[i].field_key] = fields[i].default_value
          }
          this.addForm.ticket_data = obj;
          debugger;
          console.log(this.addForm)
          createTicket(this.addForm).then((res) => {
            if (res.code >= 200) {
              this.getList();
              this.limitedAdd = false;
              this.$message.success("成功");
            }
          });
        } else {
          return false;
        }
      });
    },
    handleCancel(){
      this.limitedRetreat = false;
    },
    handleSubmit(){
      debugger;
      if(this.handleTitle === '撤回工单'){
        this.$confirm("确认撤回工单吗?", "温馨提示", {
          confirmButtonText: "确认",
          cancelButtonText: "取消",
          type: "warning",
        })
          .then(async () => {
            ticketRetreat(this.retreatId,this.handleForm).then(res=>{
              this.limitedRetreat = false;
              this.getList();
              this.$store.dispatch("user/getCount", {})
              this.$message.success("成功");
            })
          })
          .catch((err) => {
            console.error(err);
          });
      }else{
        this.$confirm("确认关闭工单吗?", "温馨提示", {
          confirmButtonText: "确认",
          cancelButtonText: "取消",
          type: "warning",
        })
          .then(async () => {
            ticketClose(this.retreatId,this.handleForm).then(res=>{
              this.limitedRetreat = false;
              this.getList();
              this.$store.dispatch("user/getCount", {})
              this.$message.success("成功");
            })
          })
          .catch((err) => {
            console.error(err);
          });
      }

    },
    handleClose(scope,index){
      if(index==='1'){
        this.handleTitle = '撤回工单';
        this.handleLabel='撤回原因';
      }else{
        this.handleTitle = '关闭工单';
        this.handleLabel='关闭原因';
      }
      this.limitedRetreat = true;
      this.retreatId = scope.row.id;
    },
    handleLogs(){},
    handlePicture(scope){
      let that = this;
      that.dialogVisible = true;
      that.watchedName = scope.row.title;
      that.watchedCreateTime = scope.row.create_time;
      that.pageForm.workflow = scope.row.workflow;
      let ticketId = scope.row.id;
      getWfFlowSteps( ticketId).then((res)=>{
        if(res.data){
          debugger;
          //流程步骤数组
          that.flowSteps = res.data;
          getTicketDetail( ticketId).then((res)=>{
            if(res.data){
              debugger;
              that.tooltip = that.createTooltip();
              that.ticketDetail = res.data;
              let state = res.data.state;
              let dat = that.flowSteps.filter((item)=>{
                return item.id==state;
              })
              that.sort = dat[0].sort;
              that.actives = that.flowSteps.indexOf(dat[0]);
              if( that.flowSteps.length-that.actives >1){}else{
                that.actives =that.flowSteps.length;
              }
              var g = new dagreD3.graphlib.Graph().setGraph({
                rankdir: 'DL',
                nodesep: 100,
                edgesep: 10,//两条线之间的距离
                ranksep: 50,//节点之间的距离
                marginx: 60,
                marginy: 20,
              });
              //获取state得到节点
              getWfStateList(that.pageForm.workflow).then((response) => {
                if (response.data) {
                  let nodes = response.data;
                  // 添加节点
                  nodes.forEach((item) => {
                    if(item.sort==that.sort){
                      g.setNode(item.id, {
                        // 节点标签
                        label: item.name,
                        // 节点形状
                        shape: 'rect',
                        toolText: item.name,
                        //节点样式
                        style: "fill:#409EFF;stroke:#000",
                        labelStyle: "fill:#000;",
                        rx :5,//矩形节点圆角度
                        ry :5
                      });
                    }else{
                      g.setNode(item.id, {
                        // 节点标签
                        label: item.name,
                        // 节点形状
                        shape: 'rect',
                        toolText: item.name,
                        //节点样式
                        style: "fill:#fff;stroke:#000",
                        labelStyle: "fill:#000;",
                        rx :5,//矩形节点圆角度
                        ry :5
                      });
                    }
                  });
                  g.nodes().forEach(function (v) {
                    console.log("Node " + v + ": " + JSON.stringify(g.node(v)));
                  });
                  //获取流转得到线  链接关系
                  getWfTransitionList(that.pageForm.workflow).then((res)=>{
                    if(res.data){
                      let transitionList = res.data;
                      transitionList.forEach((transitions)=>{
                        let transition0 = transitions;
                        debugger;
                        console.log(transition0.condition_expression.length)
                        if (transition0.condition_expression.length>0){
                          g.setNode(transition0.source_state_.id+100000, {label: "条件表达式", style: "fill: #a4d088", shape: "diamond"});
                          g.setEdge(transition0.source_state_.id, transition0.source_state_.id+100000, {
                            // 边标签
                            label: transition0.name,
                            // curve: d3.curveBasis,
                            style: "fill:#ffffff;stroke:#c0c1c3;stroke-width:1.5px"
                          });
                          let condition_expression = transition0.condition_expression;
                          condition_expression.forEach(condition_expression0=>{
                            g.setEdge(transition0.source_state_.id+100000, condition_expression0.target_state, {
                              label: condition_expression0.label,
                              // curve: d3.curveBasis,
                              style: "fill:#ffffff;stroke:#c0c1c3;stroke-width:1.5px"
                            })
                          })
                        }else{
                          g.setEdge(transition0.source_state_.id, transition0.destination_state_.id, {
                            // 边标签
                            label: transition0.name,
                            // curve: d3.curveBasis,
                            // 边样式
                            style: "fill:#ffffff;stroke:#c0c1c3;stroke-width:1.5px" // 根据后台数据来改变连线的颜色
                          });
                        }
                      })
                      g.nodes().length-1
                      g.nodes().forEach(function (v) {
                        console.log("Node " + v + ": " + JSON.stringify(g.node(v)));
                      });
                      console.log("1111111111111");
                      g.edges().forEach(function (e) {
                        console.log("Edge " + e.v + " -> " + e.w + ": " + JSON.stringify(g.edge(e)));
                      });
                      // 创建渲染器
                      let render = new dagreD3.render();
                      // 选择 svg 并添加一个g元素作为绘图容器.
                      let svg = d3.select('#mySvg');
                      let svgGroup = svg.append('g');
                      let zoom = d3.zoom()
                        .on("zoom", function() {
                          svgGroup.attr("transform", d3.event.transform);
                        });
                      svg.call(zoom);
                      // 在绘图容器上运行渲染器生成流程图.
                      render(d3.select("svg g"), g);
                      getTicketFlowlog(ticketId).then(res=> {
                        if (res.data) {
                          that.logs = res.data;
                          svgGroup
                            .selectAll('g.node')
                            .on('mouseover', (v) => {
                              // 假如当前toolText为"",则不展示
                              //这里就是自定义tooltip的内容
                              let filList = [],strList = [];
                              filList = nodes.filter((ii) => {
                                return ii.name === g.node(v).label
                              })
                              if (!filList.length) {
                                return
                              }
                              debugger;
                              console.log(filList)
                              filList.map((k) => {
                                let filte = that.logs.filter(item=>{
                                  return item.state == k.id;
                                })
                                debugger;
                                console.log(filte)
                                //每个
                                let str = '处理人：'+filte[0].participant_.name;
                                strList.push(str)
                              })
                              that.tipVisible(strList)
                            })
                            .on('mouseout', () => {
                              this.tipHidden()
                            })
                        }
                      })

                    }else{}
                  });
                }
              });
            }
          });
        }
      });
    },
    // 创建提示框
    createTooltip() {
      return d3
        .select('body')
        .append('div')
        .classed('tooltip', true)
        .style('opacity', 0)
        .style('display', 'none')
    },
    // tooltip显示
    tipVisible(textContent) {
      this.tooltip
        .transition()
        .duration(400)
        .style('opacity', 1)
        .style('display', 'block')
        .style('color', '#ffffff')
        .style('z-index', '3999')
        .style('padding', '20px 30px')
        .style('border-radius', '5px')
        .style('position', 'fixed')
        .style('background', 'rgba(0,0,0,.7)')
      this.tooltip
        .html(textContent)
        .style('left', `${d3.event.pageX + 20}px`)
        .style('top', `${d3.event.pageY-10}px`)
    },

    // tooltip隐藏
    tipHidden() {
      this.tooltip
        .transition()
        .duration(400)
        .style('opacity', 0)
        .style('display', 'none')
    },
    //处理工单
    handleDetail(scope){
      this.$router.push({name:"ticketHandle",params:{ticketId:scope.row.id,workflow:scope.row.workflow}})
    },
    //工单详情
    handleDetails(scope){
      this.$router.push({name:"ticketDetail",params:{ticketId:scope.row.id,workflow:scope.row.workflow}})
    },
    //接单
    handleGetTicket(scope){
      let ticketId = scope.row.id;
      ticketAccpet(ticketId,{}).then(res=>{
        if(res.code===200){
          this.getList();
        }
      })
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
    handleDelete(scope){
      let data = new Object(),ids=[];
      ids.push(scope.row.id);
      data.ids = ids;
      this.$confirm("确认删除该工单吗?", "温馨提示", {
        confirmButtonText: "确认",
        cancelButtonText: "取消",
        type: "warning",
      }).then(async () => {
          ticketDestory(data).then(res=>{
            if(res.code==200){
              this.getList();
            }
          })
        })
    },
    stepclick(){},
    closeMark(){
      this.dialogVisible = false;
    }
  }
  }
</script>

<style scoped>
  ::-webkit-scrollbar {
    width: 15px;
  }
  ::-webkit-scrollbar-track{
    -webkit-box-shadow: inset 0 0 6px rgba(0,0,0,.2);
    background-color: #fefefe;
    border-radius: 7px;
  }
  ::-webkit-scrollbar-thumb{
    border-radius: 7px;
    -webkit-box-shadow: inset 0 0 6px rgba(0,0,0,.5);
    background-color: #f5f5f5;
  }
  .svgMark{
    width: 100%;
    height: 100%;
    position: fixed;
    top: 0;
    right: 0;
    bottom: 0;
    left: 0;
    overflow: auto;
    margin: 0;
    z-index: 2000;
    background: rgba(0,0,0,.3);
  }
  .svgWrapper{
    background: #fff;
    width: 800px;
    margin: 10vh auto 0;
    text-align: center;
    border-radius: 2px;
    max-height: 80vh;
    overflow-y: scroll;
  }
  .svgItem{
    padding: 20px 40px 0 ;
    font-family: Helvetica Neue, Helvetica, PingFang SC, Hiragino Sans GB, Microsoft YaHei, Arial, sans-serif;
    font-size: 18px;
    display: flex;
    justify-content: space-between;
  }
  svg {
    font-size: 14px;
  }
  .node rect {
    stroke: #606266;
    fill: #fff;
  }
  .edgePath path {
    stroke: #606266;
    fill: #333;
    stroke-width: 1.5px;
  }
  .el-icon-close{
    cursor: pointer;
  }
  .listItem{
    margin-top: 15px;
    font-size: 16px;
  }
  .listItem>span{
    width: 100px;
    text-align: right;
    margin-right: 10px;
    display: inline-block;
  }



  .tooltip {
    position: absolute;
    font-size: 12px;
    text-align: left;
    border-radius: 3px;
    box-shadow: rgb(174, 174, 174) 0 0 10px;
    cursor: pointer;
    display: inline-block;
    padding: 6px;
    max-width: 300px;
    word-wrap: break-word;
    word-break: normal;
  }

  .tooltip > div {
    padding: 10px;
  }
  .node rect {
    stroke: #333;
    fill: #999;
  }
  .node {
    cursor: pointer;
  }

  .edgePath path {
    stroke: #333;
    fill: #333;
    stroke-width: 1.5px;
  }
</style>
