<template>
  <div class="app-container">
    <el-card>
      <div>
        <el-input
                v-model="listQuery.search"
                placeholder="名称"
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
      <div style="margin-top: 2px">
        <el-button type="primary" icon="el-icon-plus" @click="handleCreate">新增</el-button>
      </div>
    </el-card>
    <el-card style="margin-top: 2px">
      <el-table
        v-loading="listLoading"
        :data="workflowList.results"
        border fit stripe
        style="width: 100%"
        height="100"
        highlight-current-row
        v-el-height-adaptive-table="{bottomOffset: 50}"
      >
        <el-table-column type="index" width="50" />
        <el-table-column label="名称">
          <template slot-scope="scope">{{ scope.row.name }}</template>
        </el-table-column>
        <el-table-column label="描述">
          <template slot-scope="scope">{{ scope.row.description }}</template>
        </el-table-column>
        <el-table-column label="工单查看权限校验">
          <template slot-scope="scope">
            {{ !!(scope.row.view_permission_check)?'是':'否' }}
          </template>
        </el-table-column>
        <el-table-column width="180" label="创建时间">
          <template slot-scope="scope">{{ scope.row.create_time }}</template>
        </el-table-column>
        <el-table-column
          align="center"
          label="操作"
          width="300px"
        >
          <template slot-scope="scope">
            <el-link
              v-if="checkPermission(['workflow_update'])"
              @click="handlecfgt(scope)"
            >配置</el-link>
            <el-link
              v-if="checkPermission(['workflow_update'])"
              @click="handleEdit(scope)"
            >编辑</el-link>
            <el-link
              v-if="checkPermission(['workflow_delete'])"
              type="danger"
              @click="handleDelete(scope)"
            >删除</el-link>
            <el-link
              type="primary"
              @click="handleTicket(scope)"
            >查看工单</el-link>
            <el-link
              type="primary"
              @click="handleWatch(scope)"
            >查看流程图</el-link>
          </template>
        </el-table-column>
      </el-table>
      <pagination
        v-show="workflowList.count > 0"
        :total="workflowList.count"
        :page.sync="listQuery.page"
        :limit.sync="listQuery.page_size"
        @pagination="getList"
      />
    </el-card>
    <div class="svgMark" v-if="limitedWatch" @click="closeMark">
      <div class="svgWrapper">
        <div class="svgItem">工作流流程图<i class="el-dialog__close el-icon el-icon-close" @click="closeMark"></i></div>
        <el-row>
          <el-col :span="12">
            <p>工作流名称 ：{{watchedName}}</p>
          </el-col>
          <el-col :span="12">
            <p>创建时间 ：{{watchedCreateTime}}</p>
          </el-col>
        </el-row>
        <div style="width: 90%;margin: auto;">
          <svg height=1000 id="mySvg" style="width:100%!important;">
          </svg>
        </div>
      </div>
    </div>
    <el-dialog
      :visible.sync="dialogVisible"
      :title="dialogType === 'edit' ? '编辑工作流' : '新增工作流'">
      <el-form
        ref="Form"
        :model="workflow"
        label-width="100px"
        label-position="right"
        :rules="rule1">
        <el-form-item label="名称" prop="name">
          <el-input v-model="workflow.name" placeholder="名称" />
        </el-form-item>
        <el-form-item label="流水号前缀">
          <el-input v-model="workflow.sn_prefix " placeholder="流水号前缀" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            type="textarea"
            :rows="4"
            v-model="workflow.description"
            placeholder="描述"
          />
        </el-form-item>
        <el-form-item
          label="查看权限校验"
          prop="view_permission_check"
          label-width="120px"
        >
          <el-switch v-model="workflow.view_permission_check"></el-switch>
        </el-form-item>
        <el-form-item label="展现表单字段">
          <el-transfer
            v-model="workflow.display_form_str"
            :data="choiceOption"
            :titles="['未展示字段', '展示字段']"
            :props="{ key: 'id', label: 'field_name' }"
          />
        </el-form-item>
        <el-form-item label="标题模板" prop="title_template">
          <el-input v-model="workflow.title_template" placeholder="你有一个待办工单:{title}" />
        </el-form-item>
        <el-form-item label="内容模板" prop="content_template">
          <el-input v-model="workflow.content_template" placeholder="标题:{title}, 创建时间:{create_time}" />
        </el-form-item>
      </el-form>
      <div style="text-align: right">
        <el-button type="danger" @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirm('Form')">确认</el-button>
      </div>
    </el-dialog>
  </div>
</template>
<script src="https://d3js.org/d3.v4.min.js"></script>
<script>
  import { getWfTransitionList,getWorkflowList, createWorkflow,updateWorkflow,deleteWorkflow,getWfCustomfieldList,getWfStateList } from "@/api/workflow";
  import checkPermission from "@/utils/permission";
  // import vueJsonEditor from 'vue-json-editor'
  import Pagination from "@/components/Pagination"; // secondary package based on el-pagination
  import dagreD3 from 'dagre-d3'
  import * as d3 from 'd3'
const defaultworkflow = {
  name: "",
  number: "",
};
export default {
  components: { Pagination },
  data() {
    return {
      // workflow: defaultworkflow,
      workflow:{
        name:'',
        sn_prefix:'',
        description:'',
        view_permission_check:'',
        display_form_str:'',
        title_template:'',
        content_template:'',
      },
      limitedWatch:false,
      view_permission_check:false,
       hasJsonFlag:true,  // json是否验证通过
         hasJsonFlag1:true,  // json是否验证通过
      workflowList: {
        count: 0,
      },
      listQuery: {
        page: 1,
        page_size: 20,
      },
      choiceOption:[],
      display_form_str:[],
      limit_expression:[],
      listLoading: true,
      dialogVisible: false,
      dialogType: "new",
      watchedName:'',
      watchedCreateTime:'',
      rule1: {
        name: [{ required: true, message: "请输入", trigger: "blur" }],
        description: [{ required: true, message: "请输入", trigger: "blur" }]
      },
    };
  },
  computed: {},
  watch: {},
  created() {
    this.getList();
  },
  methods: {
    checkPermission,
    getList() {
      this.listLoading = true;
      getWorkflowList(this.listQuery).then((response) => {
        if (response.data) {
          this.workflowList = response.data;
        }
        this.listLoading = false;
      });
    },
    handleFilter() {
      this.listQuery.page = 1;
      this.getList();
    },
    resetFilter() {
      this.listQuery = {
        page: 1,
        page_size: 20,
      }
      this.getList();
    },
    handleCreate() {
      this.workflow = Object.assign({}, defaultworkflow);
      this.dialogType = "new";
      this.dialogVisible = true;
      this.$nextTick(() => {
        this.$refs["Form"].clearValidate();
      });
    },
    handleEdit(scope) {
      this.workflow = Object.assign({}, scope.row); // copy obj
      this.dialogType = "edit";
      this.dialogVisible = true;
      this.$nextTick(() => {
        this.$refs["Form"].clearValidate();
      });
      getWfCustomfieldList(scope.row.id).then((response) => {
        if (response.data) {
          this.choiceOption = response.data;
        }

      });
    },
    handlecfgt(scope)
    {
      this.$router.push({name:"configuration",params:{workflow:scope.row.id}})
    },
    handleDelete(scope) {
      this.$confirm("确认删除?", "警告", {
        confirmButtonText: "确认",
        cancelButtonText: "取消",
        type: "error",
      })
        .then(async () => {
          await deleteWorkflow(scope.row.id);
          this.getList();
          this.$message.success("成功");
        })
        .catch((err) => {
          console.error(err);
        });
    },
    handleTicket(scope){
      this.$router.push({name:"workFlowTickets",params:{workflow:scope.row.id}})
    },
    async confirm(form) {
      debugger;
      console.log(this.workflow.display_form_str)

      this.$refs[form].validate((valid) => {
        if (valid) {
          const isEdit = this.dialogType === "edit";
          if (isEdit) {
            this.checkJson();
             this.checkJson2();
            updateWorkflow(this.workflow.id, this.workflow).then((res) => {
              if (res.code >= 200) {
                this.getList();
                this.dialogVisible = false;
                this.$message.success("成功");
              }
            });
          } else {
            this.checkJson();
             this.checkJson2();
            createWorkflow(this.workflow).then((res) => {
              if (res.code >= 200) {
                this.getList();
                 this.dialogVisible = false;
                this.$message.success("成功");
              }
            });
          }
        } else {
          return false;
        }
      });
    },
    handleWatch(scope){
      let that = this;
      let workFlow = scope.row.id;
      that.watchedName = scope.row.name;
      that.watchedCreateTime = scope.row.create_time;
      that.limitedWatch = true;
      that.$nextTick(()=>{
        var g = new dagreD3.graphlib.Graph().setGraph({
          rankdir: 'DL',
          nodesep: 100,
          edgesep: 10,//两条线之间的距离
          ranksep: 50,//节点之间的距离
          marginx: 160,
          marginy: 20,
        });
        //获取state得到节点
        getWfStateList(workFlow).then((response) => {
          if (response.data) {
            let nodes = response.data;
            // 添加节点
            nodes.forEach((item) => {
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
            });
            g.nodes().forEach(function (v) {
              console.log("Node " + v + ": " + JSON.stringify(g.node(v)));
            });
            //获取流转得到线  链接关系
            getWfTransitionList(workFlow).then((res)=>{
              if(res.data){
                let transitionList = res.data;
                transitionList.forEach((transition0)=>{
                  if (transition0.condition_expression.length>0){
                    debugger;
                    g.setNode(transition0.source_state_.id+100000, {label: "条件表达式",style: "stroke: #000;fill: #afa", shape: "diamond"});
                    g.setEdge(transition0.source_state_.id, transition0.source_state_.id+100000, {
                      // 边标签
                      label: transition0.name,
                      style: "fill:#ffffff;stroke:#c0c1c3;stroke-width:1.5px"
                    });
                    let condition_expression = transition0.condition_expression;
                    condition_expression.forEach(condition_expression0=>{
                      g.setEdge(transition0.source_state_.id+100000, condition_expression0.target_state, {
                        label: condition_expression0.label,
                        style: "fill:#ffffff;stroke:#c0c1c3;stroke-width:1.5px"
                      })
                    })
                  }else{
                    g.setEdge(transition0.source_state_.id, transition0.destination_state_.id, {
                      // 边标签
                      label: transition0.name,
                      // 边样式
                      style: "fill:#ffffff;stroke:#c0c1c3;stroke-width:1.5px" // 根据后台数据来改变连线的颜色
                    });
                  }
                })
                g.nodes().length-1
                g.nodes().forEach(function (v) {
                  console.log("Node " + v + ": " + JSON.stringify(g.node(v)));
                });
                // 创建渲染器
                let render = new dagreD3.render();
                // 选择 svg 并添加一个g元素作为绘图容器.
                let svg = d3.select('#mySvg');
                let svgGroup = svg.append('g');
                // 在绘图容器上运行渲染器生成流程图.
                render(d3.select("svg g"), g);
              }else{}
            });

          }
        });

      })
    },
    closeMark(){
      this.limitedWatch = false;
    },
   onJsonChange (value) {
        // console.log('更改value:', value);
        // 实时保存
        this.onJsonSave(value)
      },
      onJsonSave (value) {
        // console.log('保存value:', value);
        this.limit_expression = value
        this.hasJsonFlag = true
      },
      onError(value) {
        this.hasJsonFlag = false
      },
       onJsonChange1 (value) {
        // 实时保存
        this.onJsonSave1(value)
      },
      onJsonSave1 (value) {
        this.display_form_str = value
        this.hasJsonFlag1 = true
      },
      onError1(value) {
        this.hasJsonFlag1 = false
      },
      // 检查json
      checkJson(){
        if (this.hasJsonFlag == false){
          // alert("限制表达式json验证失败")
          return false
        } else {
          // alert("限制表达式json验证成功")
          return true
        }
      },
       // 检查json
      checkJson2(){
        if (this.hasJsonFlag1 == false){
          // alert("展现表单字段json验证失败")
          return false
        } else {
          // alert("展现表单字段json1验证成功")
          return true
        }
      },
  },
};
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
  g.conditions > rect {
    fill: #00ffd0;
    stroke: #000;
  }
  .el-icon-close{
    cursor: pointer;
  }
</style>
