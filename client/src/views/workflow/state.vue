<template>
  <div class="app-container">
    <el-card>
      <div style="margin-top: 2px">
        <el-button type="primary" icon="el-icon-plus" @click="handleCreate">新增
        </el-button>
      </div>
    </el-card>
    <el-card style="margin-top: 2px">
      <el-table
        :data="wfstateList"
        style="width: 100%"
      >
        <el-table-column type="index" width="50"/>
        <el-table-column width="180" label="名称">
          <template slot-scope="scope">{{ scope.row.name }}</template>
        </el-table-column>
        <el-table-column width="180" label="是否隐藏">
          <template slot-scope="scope">
            {{ !!(scope.row.is_hidde)?'是':'否' }}
          </template>
        </el-table-column>
        <el-table-column width="180" label="顺序ID">
          <template slot-scope="scope">{{ scope.row.sort }}</template>
        </el-table-column>
        <el-table-column width="180" label="类型">
          <template slot-scope="scope">
            <el-tag effect="plain" v-if="scope.row.type==0">
              普通类型
            </el-tag>
            <el-tag effect="plain" v-if="scope.row.type==1">
              初始状态
            </el-tag>
            <el-tag effect="plain" v-if="scope.row.type==2">
              结束状态
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column width="180" label="参与人类型">
          <template slot-scope="scope">{{ options_[scope.row.participant_type] }}</template>
        </el-table-column>

        <el-table-column width="180" label="创建时间">
          <template slot-scope="scope">{{ scope.row.create_time }}</template>
        </el-table-column>


        <el-table-column
          align="center"
          label="操作"
          width="220px"
        >
          <template slot-scope="scope">
            <!--  v-if="checkPermission(['workflow_update'])"  -->
            <el-link
              @click="handleEdit(scope)"
            >编辑
            </el-link>
            <el-link
              type="danger"
              @click="handleDelete(scope)"
            >删除
            </el-link>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    <el-dialog
      :visible.sync="dialogVisible"
      :title="dialogType === 'edit' ? '编辑状态' : '新增状态'"
    >
      <el-form
        ref="Form"
        :model="wfstate"
        label-width="100px"
        label-position="right"
        :rules="rule1"
      >
        <el-form-item label="名称" prop="name">
          <el-input v-model="wfstate.name" placeholder="名称"/>
        </el-form-item>
        <el-form-item
          label="是否隐藏"
          prop="is_hidden"
          label-width="120px"
        >
          <el-switch v-model="wfstate.is_hidden"></el-switch>
        </el-form-item>

        <el-form-item label="状态顺序" prop="sort">
          <el-input v-model="wfstate.sort" type="number" placeholder="状态顺序"/>
        </el-form-item>
        <el-form-item label="状态类型" prop="type">

          <el-select style="width: 100%" v-model="wfstate.type" placeholder="请选择">
            <el-option
              v-for="item in options"
              :key="item.value"
              :label="item.label"
              :value="item.value">
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item
          label="允许撤回"
          prop="enable_retreat"
          label-width="120px"
        >
          <el-switch v-model="wfstate.enable_retreat"></el-switch>
        </el-form-item>
        <el-form-item label="参与者类型" prop="participant_type">
          <el-select style="width: 100%" v-model="wfstate.participant_type" placeholder="请选择" @change="typeChange">
            <el-option
              v-for="item in typeoptions"
              :key="item.value"
              :label="item.label"
              :value="item.value">
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="参与者" prop="participant" v-if="wfstate.participant_type==1">
          <el-select style="width: 100%" v-model="participant" placeholder="请选择参与者">
            <el-option v-for="item in staffs" :key="item.id" :label="item.name" :value="item.id">
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="参与者" prop="participant" v-if="wfstate.participant_type==2">
          <el-select style="width: 100%" v-model="participants" multiple placeholder="请选择参与者">
            <el-option v-for="item in staffs" :key="item.id" :label="item.name" :value="item.id">
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="参与者" prop="participant" v-if="wfstate.participant_type==7">
          <el-select style="width: 100%" v-model="participant" placeholder="请选择字段">
            <el-option v-for="item in customfieldList" :key="item.id" :label="item.field_name"
                       :value="item.field_key">
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="分配方式" prop="participant" v-if="wfstate.participant_type==2">
          <el-select style="width: 100%" v-model="wfstate.distribute_type" placeholder="请选择分配方式">
            <el-option label="主动接单" value="1"></el-option>
            <el-option label="直接处理" value="2"></el-option>
            <el-option label="随机分配" value="3"></el-option>
            <el-option label="全部处理" value="4"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="角色" prop="participant" v-if="wfstate.participant_type==4">
          <el-select style="width: 100%" v-model="participants" multiple placeholder="请选择角色">
            <el-option v-for="item in roles" :key="item.id" :label="item.name" :value="item.id">
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="过滤策略" prop="participant" v-if="wfstate.participant_type==4">
          <el-select style="width: 100%" v-model="wfstate.filter_policy" placeholder="请选择过滤策略">
            <el-option label="无" value="0"></el-option>
            <el-option label="和工单同属以及上级部门" value="1"></el-option>
            <el-option label="和创建人同属以及上级部门" value="2"></el-option>
            <el-option label="和上步处理人同属以及上级部门" value="3"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="代码选择" prop="participant" v-if="wfstate.participant_type==9">
          <el-select style="width: 100%" v-model="participants" placeholder="请选择代码">
            <el-option v-for="item in codes" :key="item.func" :label="item.name" :value="item.func">
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="抄送给" prop="participant">
          <el-select style="width: 100%" v-model="wfstate.participant_cc" multiple placeholder="请选择抄送给谁">
            <el-option v-for="item in staffs" :key="item.id" :label="item.name" :value="item.id">
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="字段状态">
          <el-button @click="addWordStatusChange">添加修改</el-button>
          <el-row v-for="(item,$index) in statusChange" :key="item+$index" style="margin-top: 2px">
            <el-col :span="11">
              <el-select style="width: 100%" v-model="item.name" placeholder="请选择字段">
                <el-option v-for="item in customfieldList" :key="item.id" :label="item.field_name"
                           :value="item.field_key">
                </el-option>
              </el-select>
            </el-col>
            <el-col :span="1" style="height: 1px;"></el-col>
            <el-col :span="8">
              <el-select style="width: 100%" v-model="item.value" placeholder="请选择状态">
                <el-option
                  v-for="item in state_fields"
                  :label="item.label"
                  :value="item.value"
                  :key="item.value"
                ></el-option>
              </el-select>
            </el-col>
            <el-col :span="2" style="text-align: center" v-if="$index!==0">
              <i
                class="el-icon-remove-outline"
                style="color: red;font-size: 16px;"
                @click.prevent="removeStatusChange($index)"
              ></i>
            </el-col>
          </el-row>
        </el-form-item>
      </el-form>
      <div style="text-align: right">
        <el-button type="danger" @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirm('Form')">确认</el-button>
      </div>
    </el-dialog>
  </div>
</template>
<script>
  import {getWfStateList, createWfState, updateWfState,
    deleteWfState, getWfCustomfieldList , getCodes } from "@/api/workflow";
  import { getUserList} from "@/api/user";
  import { getRoleAll } from "@/api/role";
  import checkPermission from "@/utils/permission";
  const defaultwfstate = {
    name: "",
  };
  export default {
    components: {},
    name: "State",
    props: ["ID"],
    data() {
      return {
        wfstate: {
          name: '',
          is_hidden: '',
          sort: '',
          type: '',
          participant_cc: [],
          enable_retreat: '',
          participant_type: '',
          filter_policy: '',
          distribute_type: '',//分发类型
          state_fields: {}//字段状态是否可写
        },
        statusChange: [],
        participant: '',
        participants: [],
        is_hidden: false,
        enable_retreat: false,
        staffs: [],
        roles: [],
        codes: [],
        customfieldList: [],
        /*wfstateList: {
          count:0
        },*/
        wfstateList: [],
        options_: {
          "0": '无处理',
          "1": '个人',
          "2": '多人',
          // "3": '部门',
          "4": '角色',
          // "5": '变量',
          "6": '脚本',
          "7": '工单的字段',
          // "8": '父工单的字段',
          "9": '代码获取',
        },
        options: [{
          value: 0,
          label: '普通类型'
        }, {
          value: 1,
          label: '初始状态'
        }, {
          value: 2,
          label: '结束状态'
        }],
        typeoptions: [{
          value: 0,
          label: '无处理'
        }, {
          value: 1,
          label: '个人'
        }, {
          value: 2,
          label: '多人'
        }
        , {
          value: 4,
          label: '角色'
        }
        , {
          value: 6,
          label: '脚本'
        }
        , {
          value: 7,
          label: '工单的字段'
        }
        , {
          value: 9,
          label: '代码获取'
        }],
        state_fields:[
          {
            value: 1,
            label: '只读'
          },{
            value: 2,
            label: '必填'
          },{
            value: 3,
            label: '可选'
          },{
            value: 4,
            label: '隐藏'
          },
        ],
        display_form_str: [],
        limit_expression: [],
        dialogVisible: false,
        dialogType: "new",
        rule1: {
          name: [{required: true, message: "请输入", trigger: "blur"}],
          sort: [{required: true, message: "请输入", trigger: "blur"}],
          type: [{required: true, message: "选择", trigger: "blur"}],

        },
      };
    },

    created() {
      this.getList();
      this.getUser();
      this.getDepartment();
    },
    mounted(){
      this.getCodes();
    },
    methods: {

      checkPermission(value){
       /* debugger;
        console.log(checkPermission(value))*/
        checkPermission(value);
      },

      getList() {

        getWfStateList(this.ID).then((response) => {

          if (response.data) {
            this.wfstateList = response.data;
          }

        });
        getWfCustomfieldList(this.ID).then((response) => {
          if (response.data) {
            this.customfieldList = response.data;
          }

        });
      },
      getUser() {
        getUserList({}).then(res => {
          if (res.data) {
            this.staffs = res.data.results;
          }
        })
      },
      getDepartment() {
        getRoleAll().then(res => {
          if (res.data) {
            this.roles = res.data;
          }
        })
      },
      getCodes(){
        getCodes().then(res=>{
          // debugger;
          // console.log(res);
          this.codes = res.data;
        })
      },
      //参与者类型变化
      typeChange() {
        this.participant = '';
        this.participants = [];
      },
      //打开新建
      handleCreate() {
        this.wfstate = Object.assign({}, defaultwfstate);
        this.dialogType = "new";
        this.dialogVisible = true;
        this.$nextTick(() => {
          this.$refs["Form"].clearValidate();
        });
      },
      //打开编辑
      handleEdit(scope) {
        this.wfstate = Object.assign({}, scope.row); // copy obj
        this.participants = this.wfstate.participant;
        this.participant = this.wfstate.participant;
        /////
        debugger;
        console.log(this.wfstate.state_fields);
        let arr = [];
        for (let pro in this.wfstate.state_fields) {
          let obj = new Object();
          obj.name = pro;
          obj.value = this.wfstate.state_fields[pro];
          arr.push(obj)
        }
        this.statusChange = arr;
        this.wfstate.distribute_type = this.wfstate.distribute_type.toString();
        this.wfstate.filter_policy = this.wfstate.filter_policy.toString();
        this.dialogType = "edit";
        this.dialogVisible = true;
        this.$nextTick(() => {
          this.$refs["Form"].clearValidate();
        });
      },
      addWordStatusChange() {
        this.statusChange.push({name: '', value: ''})
      },
      removeStatusChange(index) {
        this.statusChange.splice(index, 1)
      },
      //编辑新建
      async confirm(form) {
        this.$refs[form].validate((valid) => {
          if (valid) {
            const isEdit = this.dialogType === "edit";
            // this.wfstate.participant = 1;
            let state_fields = {};
            if (this.statusChange.length > 0) {
              for (let i = 0; i < this.statusChange.length; i++) {
                state_fields[this.statusChange[i].name] = this.statusChange[i].value;
              }
            }
            debugger;
            console.log(state_fields);
            this.wfstate.state_fields = state_fields;
            this.wfstate.participant = this.wfstate.participant_type === 1 ? this.participant : this.participants;
            if (isEdit) {
              updateWfState(this.wfstate.id, this.wfstate).then((res) => {
                if (res.code >= 200) {
                  this.getList();
                  this.dialogVisible = false;
                  this.$message.success("成功");
                  this.getList();
                }
              });
            } else {
              this.wfstate.workflow = this.ID;
              createWfState(this.wfstate).then((res) => {
                if (res.code >= 200) {
                  this.getList();
                  this.dialogVisible = false;
                  this.getList();
                  this.$message.success("成功");
                }
              });
            }
          } else {
            return false;
          }
        });
      },


      handleDelete(scope) {
        this.$confirm("确认删除?", "警告", {
          confirmButtonText: "确认",
          cancelButtonText: "取消",
          type: "error",
        })
          .then(async () => {
            await deleteWfState(scope.row.id);
            this.getList();
            this.$message.success("成功");
          })
          .catch((err) => {
            console.error(err);
          });
      },


    },
  };
</script>
