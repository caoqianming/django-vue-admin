<template>
  <div class="app-container">
    <el-card>
      <div style="margin-top: 2px">
        <el-button type="primary" icon="el-icon-plus" @click="handleCreate"
        >新增
        </el-button>
      </div>
    </el-card>
    <el-card style="margin-top: 2px">
      <el-table

        :data="customfieldList"
        style="width: 100%"
      >
        <el-table-column type="index" width="50"/>
        <el-table-column label="字段标识">
          <template slot-scope="scope">{{ scope.row.field_key }}</template>
        </el-table-column>
        <el-table-column label="字段名称">
          <template slot-scope="scope">{{ scope.row.field_name }}</template>
        </el-table-column>
        <el-table-column label="字段类型">
          <template slot-scope="scope">{{ scope.row.field_type }}</template>
        </el-table-column>
        <el-table-column label="顺序ID">
          <template slot-scope="scope">{{ scope.row.sort }}</template>
        </el-table-column>
        <el-table-column label="字段描述">
          <template slot-scope="scope">{{ scope.row.description }}</template>
        </el-table-column>
        <el-table-column label="创建时间">
          <template slot-scope="scope">{{ scope.row.create_time }}</template>
        </el-table-column>

        <el-table-column
          align="center"
          label="操作"
          width="220px"
        >
          <template slot-scope="scope">

            <el-link
              v-if="checkPermission(['customfield_update'])"
              @click="handleEdit(scope)"
            >编辑
            </el-link
            >
            <el-link
              v-if="checkPermission(['customfield_delete'])"
              type="danger"
              @click="handleDeleteCustomfield(scope)"
            >删除
            </el-link
            >
          </template>
        </el-table-column>
      </el-table>

    </el-card>
    <el-dialog
      :visible.sync="dialogVisible"
      :title="dialogType === 'edit' ? '编辑自定义字段' : '新增自定义字段'">
      <el-form
        ref="Form"
        :model="customfield"
        label-width="80px"
        label-position="right"
        :rules="rule1">
        <el-form-item label="字段标识" prop="field_key">
          <el-input v-model="customfield.field_key" placeholder="字段标识"/>
        </el-form-item>
        <el-form-item label="字段名称" prop="field_name">
          <el-input v-model="customfield.field_name" placeholder="字段名称"/>
        </el-form-item>
        <el-form-item label="字段描述" prop="description">
          <el-input v-model="customfield.description" placeholder="字段描述"/>
        </el-form-item>
        <el-form-item label="占位符" prop="placeholder">
          <el-input v-model="customfield.placeholder" placeholder="占位符"/>
        </el-form-item>
        <el-form-item label="展示标签" prop="field_type">
          <el-select style="width: 100%" v-model="customfield.field_type" placeholder="请选择">
            <el-option
              v-for="item in options"
              :key="item.value"
              :label="item.label"
              :value="item.value">
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="字段标签" v-show="customfield.field_type=='select'||customfield.field_type=='selects'">
          <el-input v-model="customfield.label" placeholder="选项类型"/>
        </el-form-item>
        <el-form-item label="选项" v-show="customfield.field_type=='select'||customfield.field_type=='selects'">
          <el-button @click.prevent="addDomain" style="border: none;">
            <i class="el-icon-circle-plus-outline"></i>
            <span style="font-size:14px;">添加</span>
          </el-button>
          <el-row v-for="(domain, $index) in choiceOption" :key='$index+1' style="margin-bottom: 10px">
            <el-col :span="10">
              <template>
                <el-form-item label="id：">
                  <el-input type="number" v-model="choiceOption[$index].id" auto-complete="off" placeholder="id为整数"></el-input>
                </el-form-item>
              </template>
            </el-col>
            <el-col :span="10">
              <template>
                <el-form-item label="name：">
                  <el-input v-model="choiceOption[$index].name" auto-complete="off"></el-input>
                </el-form-item>
              </template>

            </el-col>
            <el-col :span="3" style="text-align: center" v-if="$index!==0">
              <i
                class="el-icon-remove-outline"
                style="color: red;font-size: 16px;"
                @click.prevent="removeDomain($index,'1')"
              ></i>
            </el-col>
          </el-row>
        </el-form-item>
        <el-form-item label="顺序ID">
          <el-input v-model="customfield.sort" type="number" placeholder="顺序"/>
        </el-form-item>
        <el-form-item label="默认值">
          <el-input v-model="customfield.default_value" placeholder="默认值"/>
        </el-form-item>
        <el-form-item label="模板">
          <el-input v-model="customfield.field_template" placeholder="你有一个待办工单:{title}"/>
        </el-form-item>
        <el-form-item label="是否隐藏">
          <el-radio-group v-model="customfield.is_hidden">
            <el-radio :label="false">显示</el-radio>
            <el-radio :label="true">隐藏</el-radio>
          </el-radio-group>
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
  import {getWfCustomfieldList, createWfCustomfield, updateWfCustomfield, deleteWfCustomfield} from "@/api/workflow";
  import checkPermission from "@/utils/permission";
  import vueJsonEditor from 'vue-json-editor'
  import Pagination from "@/components/Pagination"; // secondary package based on el-pagination
  const defaultcustomfield = {
    field_key: "",
    field_name: "",
  };
  export default {
    components: {Pagination, vueJsonEditor},
    name: "CTF",
    props: ["ID"],
    data() {
      return {
        customfield: {
          field_key: '',
          field_name: '',
          placeholder: '',
          field_type: '',
          sort: '',
          label: 'name',
          default_value: '',
          field_template: '',
          field_choice: [],
          is_hidden:false,
        },
        fieldHidden: true,
        fieldBlock: false,
        view_permission_check: false,
        hasJsonFlag: true,  // json是否验证通过
        hasJsonFlag1: true,  // json是否验证通过
        hasJsonFlag2: true,  // json是否验证通过
        // customfieldList: {
        //    count:0
        // },
        customfieldList: [''],
        labels:[{
          label: '常规',
          value: 'name'
        },{
          label: '名称|id',
          value: 'name|id'
        },{
          label: '人员选择',
          value: 'user'
        }],
        options: [{
          value: 'string',
          label: '文本'
        }, {
          value: 'int',
          label: '整数'
        }, {
          value: 'float',
          label: '小数'
        }, {
          value: 'date',
          label: '日期'
        }, {
          value: 'datetime',
          label: '日期时间'
        }, {
          value: 'select',
          label: '单选'
        }, {
          value: 'selects',
          label: '多选'
        }, {
          value: 'textarea',
          label: '文本域'
        },{
          value: 'file',
          label: '附件'
        }],
        /*, {
          value: 'selectuser',
          label: '用户名'
        }, {
          value: 'selectusers',
          label: '多选的用户名'
        }, */


        boolean_field_display: [],
        choiceOption: [{id:null,name:""}],
        field_choice: [],
        dialogVisible: false,
        dialogType: "new",
        rule1: {
          name: [{required: true, message: "请输入", trigger: "blur"}],
          description: [{required: true, message: "请输入", trigger: "blur"}]
        },
      };
    },
    computed: {},
    watch: {},
    created() {
      this.getList();
    },
    methods: {
      //添加字段选项
      addDomain() {
        this.choiceOption.push({id:null,name:""})
      },
      //删除字段选项
      removeDomain(index) {
        this.choiceOption.splice(index, 1)
      },
      checkPermission,

      getList() {
        getWfCustomfieldList(this.ID).then((response) => {
          if (response.data) {
            this.customfieldList = response.data;
          }

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
        this.customfield = Object.assign({}, defaultcustomfield);
        this.dialogType = "new";
        this.dialogVisible = true;
        /*this.$nextTick(() => {
          // this.$refs["Form"].clearValidate();
          this.customfield.label = 1;
        });*/
      },

      handleEdit(scope) {
        debugger;
        this.customfield = Object.assign({}, scope.row); // copy obj
        this.choiceOption = scope.row.field_choice;
        this.dialogType = "edit";
        this.dialogVisible = true;
        /*this.$nextTick(() => {
          this.$refs["Form"].clearValidate();
        });*/
      },
      handlecfgt(scope) {
        this.$router.push({name: "configuration", params: {customfield: scope.row.id}})
      }
      ,
      handleDelete(scope) {
        this.$confirm("确认删除?", "警告", {
          confirmButtonText: "确认",
          cancelButtonText: "取消",
          type: "error",
        })
          .then(async () => {
            await this.deleteWorkflow(scope.row.id);
            this.getList();
            this.$message.success("成功");
          })
          .catch((err) => {
            console.error(err);
          });
      },

      async confirm(form) {
        let that = this,choiceArr = [];
        this.$refs[form].validate((valid) => {
          if (valid) {
            const isEdit = that.dialogType === "edit";
            if(that.choiceOption[0]&&that.choiceOption[0].name!==''&&that.choiceOption[0].name!==null&&that.choiceOption[0].name!==undefined){
              that.choiceOption.forEach((item)=>{
                let obj = new Object();
                obj.id = parseInt(item.id);
                obj.name = item.name;
                choiceArr.push(obj);
              })
            }
            debugger;
            console.log(choiceArr);
            that.customfield.field_choice = choiceArr;
            console.log(that.customfield);
            if (isEdit) {
              updateWfCustomfield(this.customfield.id, this.customfield).then((res) => {
                if (res.code >= 200) {
                  this.getList();
                  this.dialogVisible = false;
                  this.$message.success("成功");
                }
              });
            } else {
              this.customfield.workflow = this.ID;
              createWfCustomfield(this.customfield).then((res) => {
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
      handleDeleteCustomfield(scope) {
        this.$confirm("确认删除?", "警告", {
          confirmButtonText: "确认",
          cancelButtonText: "取消",
          type: "error",
        })
          .then(async () => {
            await deleteWfCustomfield(scope.row.id);
            this.getList();
            this.$message.success("成功");
          })
          .catch((err) => {
            console.error(err);
          });
      },

     /* onJsonChange(value) {
        // console.log('更改value:', value);
        // 实时保存
        this.onJsonSave(value)
      },
      onJsonSave(value) {
        // console.log('保存value:', value);
        this.boolean_field_display = value
        this.hasJsonFlag = true
      },
      onError(value) {
        // console.log("json错误了value:", value);
        this.hasJsonFlag = false
      },

      // 检查json
      checkJson() {
        if (this.hasJsonFlag == false) {
          // alert("布尔显示定义json验证失败")
          return false
        } else {
          // alert("布尔显示定义json验证成功")
          return true
        }
      },
      onJsonChange1(value) {
        // console.log('更改value:', value);
        // 实时保存
        this.onJsonSave1(value)
      },
      onJsonSave1(value) {
        this.field_choice = value
        this.hasJsonFlag1 = true
      },
      onError1(value) {
        this.hasJsonFlag1 = false
      },
      // 检查json
      checkJson1() {
        if (this.hasJsonFlag1 == false) {
          // alert("选项json验证失败")
          return false
        } else {
          // alert("选项json1验证成功")
          return true
        }
      },
      onJsonChange2(value) {
        // console.log('更改value:', value);
        // 实时保存
        this.onJsonSave2(value)
      },
      onJsonSave2(value) {
        this.field_choice = value
        this.hasJsonFlag2 = true
      },
      onError2(value) {
        this.hasJsonFlag2 = false
      },
      // 检查json
      checkJson2() {
        if (this.hasJsonFlag2 == false) {
          // alert("标签json验证失败")
          return false
        } else {
          // alert("标签json1验证成功")
          return true
        }*/
      // },


    },
  };
</script>
