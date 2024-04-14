<template>
  <div class="app-container">
    <el-card>
      <div>
        <el-button type="primary" icon="el-icon-plus" @click="handleCreate">新增卡片</el-button>
        <el-select v-model="listQuery.region" placeholder="卡片类型" style="width: 120px">
          <el-option v-for="(item, index) in typeOptions" :key="index" :label="item.label"
                     :value="item.value"></el-option>
        </el-select>
        <el-input
          v-model="listQuery.search"
          placeholder="分组"
          style="width: 120px"
          class="filter-item"
          @keyup.enter.native="handleFilter"
        />
        <el-input v-model="listQuery.field110" style="width: 120px" placeholder="输入卡片ID"></el-input>
        <el-input v-model="listQuery.field110" style="width: 150px" placeholder="卡片完整名称"></el-input>
        <el-button
          class="filter-item"
          type="primary"
          icon="el-icon-search"
          @click="handleFilter"
        >查询
        </el-button
        >
      </div>
    </el-card>
    <el-card>
      <el-table v-loading="listLoading"
                :data="cardList.results"
                border fit stripe
                style="width: 100%"
                height="100"
                highlight-current-row
                v-el-height-adaptive-table="{bottomOffset: 50}">
        <el-table-column label="id" width="50">
          <template slot-scope="scope">{{ scope.row.name }}</template>
        </el-table-column>
        <el-table-column label="标题">
          <template slot-scope="scope">{{ scope.row.description }}</template>
        </el-table-column>
        <el-table-column label="类型">
          <template slot-scope="scope">{{ scope.row.create_time }}</template>
        </el-table-column>
        <el-table-column label="分组">
          <template slot-scope="scope">
            {{ 人工智能 }}
          </template>
        </el-table-column>
        <el-table-column label="难度">
          <template slot-scope="scope">
            {{ 简单 }}
          </template>
        </el-table-column>
        <el-table-column label="话题">
          <template slot-scope="scope">
            {{ 话题 }}
          </template>
        </el-table-column>
        <el-table-column label="状态">
          <template slot-scope="scope">
            {{ 状态 }}
          </template>
        </el-table-column>
        <el-table-column label="预览链接">
          <template slot-scope="scope">
            {{ 预览 }}
          </template>
        </el-table-column>
        <el-table-column
          align="center"
          label="操作"
        >
          <template slot-scope="scope">
            <el-link
              v-if="checkPermission(['workflow_update'])"
              @click="handlecfgt(scope)"
            >配置
            </el-link>
            <el-link
              type="primary"
              @click="handleTicket(scope)"
            >编辑
            </el-link>
          </template>
        </el-table-column>
        <pagination
          v-show="cardList.count > 0"
          :total="cardList.count"
          :page.sync="listQuery.page"
          :limit.sync="listQuery.page_size"
          @pagination="getList"
        />
      </el-table>
    </el-card>
    <el-dialog
      :visible.sync="dialogVisible"
      :title="dialogType === 'edit' ? '编辑课程' : '新增卡片'">
      <el-form
        ref="Form"
        :model="card"
        label-width="100px"
        label-position="right"
        :rules="rule1">
        <el-form-item label="卡片标题" prop="name">
          <el-input v-model="card.title" placeholder="卡片标题" style="width: 150px"/>
        </el-form-item>
        <el-form-item label="卡片类型">
          <el-select v-model="card.type" placeholder="卡片类型" style="width: 150px">
            <el-option v-for="(item, index) in typeOptions" :key="index" :label="item.label"
                       :value="item.value"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="分组" prop="description">
          <el-input v-model="card.sn_prefix " placeholder="分组" style="width: 150px"/>
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="card.status" @change="changeStatus">
            <el-radio label="1">下线</el-radio>
            <el-radio label="2">上线</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="卡片核心图" prop="dept">
          <el-upload
            class="avatar-uploader"
            :action="upUrl"
            accept="image/jpeg, image/gif, image/png, image/bmp"
            :show-file-list="false"
            :on-success="handleAvatarSuccess"
            :before-upload="beforeAvatarUpload"
            :headers="upHeaders">
            <img v-if="card.avatar" :src="card.avatar" class="avatar"/>
            <i v-else class="el-icon-plus avatar-uploader-icon"/>
          </el-upload>
        </el-form-item>
        <el-form-item label="话题" prop="description">
          <el-input v-model="card.sn_prefix " placeholder="话题" style="width: 150px"/>
        </el-form-item>
        <el-form-item label="难度">
          <el-select v-model="card.difficulty" placeholder="难度" style="width: 150px">
            <el-option v-for="(item, index) in difficultyOptions" :key="index" :label="item.label"
                       :value="item.value"></el-option>
          </el-select>
        </el-form-item>
      </el-form>
      <div style="text-align: right">
        <!--
                <el-button type="danger" @click="dialogVisible = false">取消</el-button>
        -->
        <el-button type="primary" @click="confirm('Form')">保存</el-button>
      </div>
    </el-dialog>
  </div>
</template>
<script src="https://d3js.org/d3.v4.min.js">
</script>
<script>
import {
  getWfTransitionList,
  getWorkflowList,
  createWorkflow,
  updateWorkflow,
  deleteWorkflow,
  getWfCustomfieldList,
  getWfStateList
} from "@/api/workflow";
import {getCardList} from "@/api/card";
import checkPermission from "@/utils/permission";
// import vueJsonEditor from 'vue-json-editor'
import Pagination from "@/components/Pagination"; // secondary package based on el-pagination
import dagreD3 from 'dagre-d3'
import * as d3 from 'd3'

const defaultData = {
  name: "",
  number: "",
};
export default {
  components: {Pagination},
  data() {
    return {
      tableData: {
        title: "",
        type: "",
        status: "",
        card_core_image: "",
        topic: "",
        difficulty: "",
        group_name: ""
      },
      difficultyOptions: [
        {
          "label": "简单",
          "value": 'easy'
        }, {
          "label": "中等",
          "value": 'medium'
        }, {
          "label": "困难",
          "value": 'difficult'
        }],
      typeOptions: [
        {
          "label": "单词卡片",
          "value": 1
        }, {
          "label": "语法卡片",
          "value": 2
        }],
      limitedWatch: false,
      view_permission_check: false,
      hasJsonFlag: true,  // json是否验证通过
      hasJsonFlag1: true,  // json是否验证通过
      cardList: {
        count: 0,
      },
      listQuery: {
        page: 1,
        page_size: 20,
      },
      choiceOption: [],
      display_form_str: [],
      limit_expression: [],
      listLoading: true,
      dialogVisible: false,
      dialogType: "new",
      watchedName: '',
      watchedCreateTime: '',
      rule1: {
        title: [{required: true, message: "请输入", trigger: "blur"}],
        type: [{required: true, message: "请选择", trigger: "blur"}],
        status: [{required: true, message: "请选择", trigger: "blur"}],
        card_core_image: [{required: true, message: "请上传", trigger: "blur"}],
        topic: [{required: true, message: "请输入", trigger: "blur"}],
        difficulty: [{required: true, message: "请选择", trigger: "blur"}]
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
      getCardList(this.listQuery).then((response) => {
        if (response.data) {
          this.tableDataList = response.data;
        }
        this.listLoading = false;
      });
    },
    changeStatus(value) {
      this.tableData.type = value;
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
      this.workflow = Object.assign({}, defaultData);
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
    handlecfgt(scope) {
      this.$router.push({name: "configuration", params: {workflow: scope.row.id}})
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
    handleTicket(scope) {
      this.$router.push({name: "workFlowTickets", params: {workflow: scope.row.id}})
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
    handleWatch(scope) {
      let that = this;
      let workFlow = scope.row.id;
      that.watchedName = scope.row.name;
      that.watchedCreateTime = scope.row.create_time;
      that.limitedWatch = true;
      that.$nextTick(() => {
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
                rx: 5,//矩形节点圆角度
                ry: 5
              });
            });
            g.nodes().forEach(function (v) {
              console.log("Node " + v + ": " + JSON.stringify(g.node(v)));
            });
            //获取流转得到线  链接关系
            getWfTransitionList(workFlow).then((res) => {
              if (res.data) {
                let transitionList = res.data;
                transitionList.forEach((transition0) => {
                  if (transition0.condition_expression.length > 0) {
                    debugger;
                    g.setNode(transition0.source_state_.id + 100000, {
                      label: "条件表达式",
                      style: "stroke: #000;fill: #afa",
                      shape: "diamond"
                    });
                    g.setEdge(transition0.source_state_.id, transition0.source_state_.id + 100000, {
                      // 边标签
                      label: transition0.name,
                      style: "fill:#ffffff;stroke:#c0c1c3;stroke-width:1.5px"
                    });
                    let condition_expression = transition0.condition_expression;
                    condition_expression.forEach(condition_expression0 => {
                      g.setEdge(transition0.source_state_.id + 100000, condition_expression0.target_state, {
                        label: condition_expression0.label,
                        style: "fill:#ffffff;stroke:#c0c1c3;stroke-width:1.5px"
                      })
                    })
                  } else {
                    g.setEdge(transition0.source_state_.id, transition0.destination_state_.id, {
                      // 边标签
                      label: transition0.name,
                      // 边样式
                      style: "fill:#ffffff;stroke:#c0c1c3;stroke-width:1.5px" // 根据后台数据来改变连线的颜色
                    });
                  }
                })
                g.nodes().length - 1
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
              } else {
              }
            });

          }
        });

      })
    },
    closeMark() {
      this.limitedWatch = false;
    },
    onJsonChange(value) {
      // console.log('更改value:', value);
      // 实时保存
      this.onJsonSave(value)
    },
    onJsonSave(value) {
      // console.log('保存value:', value);
      this.limit_expression = value
      this.hasJsonFlag = true
    },
    onError(value) {
      this.hasJsonFlag = false
    },
    onJsonChange1(value) {
      // 实时保存
      this.onJsonSave1(value)
    },
    onJsonSave1(value) {
      this.display_form_str = value
      this.hasJsonFlag1 = true
    },
    onError1(value) {
      this.hasJsonFlag1 = false
    },
    // 检查json
    checkJson() {
      if (this.hasJsonFlag == false) {
        // alert("限制表达式json验证失败")
        return false
      } else {
        // alert("限制表达式json验证成功")
        return true
      }
    },
    // 检查json
    checkJson2() {
      if (this.hasJsonFlag1 == false) {
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

::-webkit-scrollbar-track {
  -webkit-box-shadow: inset 0 0 6px rgba(0, 0, 0, .2);
  background-color: #fefefe;
  border-radius: 7px;
}

::-webkit-scrollbar-thumb {
  border-radius: 7px;
  -webkit-box-shadow: inset 0 0 6px rgba(0, 0, 0, .5);
  background-color: #f5f5f5;
}

.svgMark {
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
  background: rgba(0, 0, 0, .3);
}

.svgWrapper {
  background: #fff;
  width: 800px;
  margin: 10vh auto 0;
  text-align: center;
  border-radius: 2px;
  max-height: 80vh;
  overflow-y: scroll;
}

.svgItem {
  padding: 20px 40px 0;
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

.el-icon-close {
  cursor: pointer;
}
</style>
