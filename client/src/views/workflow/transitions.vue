<template>
  <div class="app-container">
    <el-card>
      
    <div style="margin-top: 2px">
      <el-button type="primary" icon="el-icon-plus" @click="handleCreate"
        >新增</el-button
      >
    </div>
    </el-card>
    <el-card style="margin-top: 2px">
      <el-table
        :data="wftransitionList"
        style="width: 100%"
      >
        <el-table-column type="index" width="50" />
        <el-table-column width="180" label="名称">
          <template slot-scope="scope">{{ scope.row.name }}</template>
        </el-table-column>
         
        <el-table-column width="180" label="定时器（单位秒）">
          <template slot-scope="scope">{{ scope.row.timer }}</template>
        </el-table-column>
        <el-table-column width="180" label="源状态">
          <template slot-scope="scope">
            <span v-if="scope.row.source_state_">{{scope.row.source_state_.name}}</span>
          </template>
        </el-table-column>
        <el-table-column width="180" label="目的状态">
          <template slot-scope="scope">
            <span v-if="scope.row.destination_state_">{{scope.row.destination_state_.name}}</span>
          </template>
        </el-table-column>
         <el-table-column  width="180" label="创建时间">
          <template slot-scope="scope">{{ scope.row.create_time }}</template>
        </el-table-column>
       

        <el-table-column
          align="center"
          label="操作"
          width="220px"
        >
          <template slot-scope="scope">
            <el-link
              v-if="checkPermission(['wftransition_update'])"
              @click="handleEdit(scope)"
              >编辑</el-link
            >
            <el-link
              v-if="checkPermission(['wftransition_delete'])"
              type="danger"
              @click="handleDelete(scope)"
              >删除</el-link
            >
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
        :model="wftransition"
        label-width="130px"
        label-position="right"
        :rules="rule1"
      >
        <el-form-item label="名称" prop="name">
          <el-input v-model="wftransition.name" placeholder="名称" />
        </el-form-item>
         <el-form-item label="定时器（单位秒）" prop="timer">
          <el-input v-model="wftransition.timer" type="number" placeholder="0" />
        </el-form-item>
           <el-form-item label="源状态" prop="source_state">
         
          <el-select v-model="wftransition.source_state" placeholder="请选择" style="width:100%">
            <el-option
              v-for="item in stateoptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
         <el-form-item label="目的状态" prop="destination_state">
            <el-select v-model="wftransition.destination_state" placeholder="请选择" style="width:100%">
            <el-option
              v-for="item in stateoptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="条件表达式" prop="condition_expression">
          <vue-json-editor
            v-model="wftransition.condition_expression"
            :showBtns="false"
            :mode="'code'"
            lang="zh"
          />
        </el-form-item>
         <el-form-item label="属性类型" prop="attribute_type">
           <el-select  style="width: 100%" v-model="wftransition.attribute_type" placeholder="请选择">
             <el-option
                v-for="item in options"
                :key="item.value"
                :label="item.label"
               :value="item.value">
              </el-option>
          </el-select>
        </el-form-item>
         <el-form-item label="是否校验必填" prop="field_require_check">
             <el-switch v-model="wftransition.field_require_check"></el-switch>
         
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
import {getWfStateList, getWfTransitionList, createWfTransition,updateWfTransition,deleteWfTransition } from "@/api/workflow";
import checkPermission from "@/utils/permission";
import vueJsonEditor from 'vue-json-editor'
import { genTree } from "@/utils"
const defaultwftransition = {
  name: "",
};
export default {
  components: { vueJsonEditor },
  name: "TST",
  props: ["ID"],
  data() {
    return {
      wftransition: defaultwftransition,
      condition_expression:false,
      /*wftransitionList: {
        count:0
      },*/
      wftransitionList:[],
      lable:'',
      options_:[],
       options: [{
          value: 1,
          label: '同意'
        }, {
          value: 2,
          label: '拒绝'
        }, {
          value: 3,
          label: '其他'
        }],
     
      stateoptions:[],
      dialogVisible: false,
      dialogType: "new",
      rule1: {
        name: [{ required: true, message: "请输入", trigger: "blur" }],
        

      },
    };
  },
 
  created() {
     

     this.getWfStateList();
     this.getList();
  },
  methods: {
    checkPermission,
   
    getList() {
    
      getWfTransitionList(this.ID).then((response) => {

        if (response.data) {
          this.wftransitionList = response.data;
        }
        
      });
    },
     getWfStateList() {
    
      getWfStateList(this.ID).then((response) => {
       
        if (response.data) {
          this.stateoptions = genTree(response.data);
        }
       
      });
    },
    
   
    handleCreate() {
      this.wftransition = Object.assign({}, defaultwftransition);
      this.dialogType = "new";
      this.dialogVisible = true;
      this.$nextTick(() => {
        this.$refs["Form"].clearValidate();
      });
    },
   
    handleEdit(scope) {
      this.wftransition = Object.assign({}, scope.row); // copy obj
      this.dialogType = "edit";
      this.dialogVisible = true;
      // this.wftransition.condition_expression = JSON.stringify(scope.row.condition_expression)
      // this.$nextTick(() => {
      //   this.$refs["Form"].clearValidate();
      // });
    },
    async confirm(form) {
      this.$refs[form].validate((valid) => {
        if (valid) {
          const isEdit = this.dialogType === "edit";
          if (isEdit) {
            updateWfTransition(this.wftransition.id, this.wftransition).then((res) => {
              if (res.code >= 200) {
                this.getList();
                this.dialogVisible = false;
                this.$message.success("成功");
              }
            });
          } else {
            this.wftransition.workflow=this.ID;
            createWfTransition(this.wftransition).then((res) => {
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
   handleDelete(scope) {
      this.$confirm("确认删除?", "警告", {
        confirmButtonText: "确认",
        cancelButtonText: "取消",
        type: "error",
      })
        .then(async () => {
          await deleteWfTransition(scope.row.id);
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
