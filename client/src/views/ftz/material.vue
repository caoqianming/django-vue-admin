<template>
  <div class="app-container">
    <el-card>
      <div>
        <el-button type="primary" icon="el-icon-plus" @click="handleAdd">新增素材</el-button>
        <el-select v-model="listQuery.type"
                   placeholder="素材类型"
                   clearable
                   style="width: 120px">
          <el-option v-for="(item, index) in typeOptions" :key="index" :label="item.name"
                     :value="item.value"></el-option>
        </el-select>
        <el-input v-model="listQuery.search" style="width: 300px" placeholder="输入关键字搜索"></el-input>
        <el-button
          class="filter-item"
          type="primary"
          icon="el-icon-search"
          @click="resetFilter"
        >查询
        </el-button
        >
      </div>
    </el-card>

    <el-table
      v-loading="listLoading"
      :data="
        tableDataList.filter(
          (data) =>
            !this.listQuery.search || data.title.toLowerCase().includes(this.listQuery.search.toLowerCase())
        )
      "
      style="width: 100%; margin-top: 10px"
      highlight-current-row
      row-key="id"
      height="100"
      stripe
      border
      v-el-height-adaptive-table="{ bottomOffset: 50 }"
    >
    <el-table-column label="ID" width="60">
      <template slot-scope="scope">{{ scope.row.id }}</template>
    </el-table-column>
    <el-table-column label="素材类型">
      <template slot-scope="scope">{{ scope.row.type }}</template>
    </el-table-column>
    <el-table-column label="标题">
      <template slot-scope="scope">{{ scope.row.title }}</template>
    </el-table-column>
    <el-table-column label="副标题">
      <template slot-scope="scope">{{ scope.row.sub_title }}</template>
    </el-table-column>
    <el-table-column label="描述">
      <template slot-scope="scope">{{ scope.row.description }}</template>
    </el-table-column>
    <el-table-column label="预览链接">
      <template slot-scope="scope">{{ scope.row.id }}</template>
    </el-table-column>
    <el-table-column label="创建日期">
      <template slot-scope="scope">
        <span>{{ scope.row.create_time }}</span>
      </template>
    </el-table-column>
    <el-table-column label="创建更新时间">
       <template slot-scope="scope">
        <span>{{ scope.row.update_time }}</span>
      </template>
    </el-table-column>
      <el-table-column align="center" label="操作">
        <template slot-scope="scope">
          <el-button
            type="primary"
            size="small"
            icon="el-icon-edit"
            :disabled="!checkPermission(['position_update'])"
            @click="handleEdit(scope)"
          />
          <el-button
            type="danger"
            size="small"
            icon="el-icon-delete"
            :disabled="!checkPermission(['position_delete'])"
            @click="handleDelete(scope)"
          />
        </template>
      </el-table-column>
    </el-table>
    <el-dialog
      :visible.sync="dialogVisible"
      :title="dialogType === 'edit' ? '编辑素材' : '新增素材'"
    >
      <el-form
        ref="Form"
        :model="tableData"
        label-width="80px"
        label-position="right"
      >
        <el-form-item label="标题" prop="title">
          <el-input v-model="tableData.title" placeholder="标题"/>
        </el-form-item>
        <el-form-item label="副标题" prop="sub_title">
          <el-input v-model="tableData.sub_title" placeholder="副标题"/>
        </el-form-item>
        <el-form-item label="素材类型" prop="type">
          <el-select
            v-model="tableData.type"
            placeholder="请选择"
            style="width: 90%"
          >
            <el-option
              v-for="item in typeOptions"
              :key="item.value"
              :label="item.name"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="内容" prop="group_name">
          <el-input v-model="tableData.content" placeholder="内容"/>
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="tableData.description" placeholder="描述" :autosize="{ minRows: 2, maxRows: 4 }"
                    type="textarea"/>
        </el-form-item>
      </el-form>
      <span slot="footer">
        <el-button type="danger" @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirm('Form')">确认</el-button>
      </span>
  </el-dialog>
  </div>
</template>

<script>
import {
  getMaterialById,
  getMaterialList,
  createMaterial,
  updateMaterial,
  deleteMaterial
} from "@/api/material";
import {getEnumConfigList} from "@/api/enum_config"
import {genTree, deepClone} from "@/utils";
import checkPermission from "@/utils/permission";
import {upUrl,upHeaders} from "@/api/file";

const defaultM = {
  title: "",
  type: "",
  description: "",
  sub_title: "",
  context: ""
};
export default {
  data() {
    return {
      upHeaders: upHeaders(),
      upUrl: upUrl(),
      tableData: {
        id: "",
        title: "",
        type: "",
        description: "",
        sub_title: "",
        context: ""
      },
      tableDataList: [],
      listLoading: true,
      dialogVisible: false,
      dialogType: "new",
      typeOptions: [
        ],
      listQuery: {
        page: 1,
        page_size: 20,
        search: null
      },
      enumConfigQuery: {
        module: 'material',
        service: 'type'
      }
    };
  },
  computed: {},
  created() {
    this.getList()
    this.getMateriaTypeList()
  },
  methods: {
    checkPermission,
    changeStatus(value) {
      this.tableData.status = value
    },
    handleAvatarSuccess(res) {
      console.log(res)
      this.tableData.card_core_image = res.data.file
    },
    beforeAvatarUpload(file) {
      const isLt2M = file.size / 1024 / 1024 < 2;
      if (!isLt2M) {
        this.$message.error("上传核心图片大小不能超过 2MB!");
      }
      return isLt2M;
    },
    getMateriaTypeList(){
      getEnumConfigList(this.enumConfigQuery).then((response) => {
        this.typeOptions = response.data;
      })
    },
    getList() {
      this.listLoading = true;
      getMaterialList(this.listQuery).then((response) => {
        this.tableDataList = response.data;
        this.tableData = response.data;
        this.listLoading = false;
      })
    },
    resetFilter() {
      this.getList(this.listQuery)
    },
    handleFilter() {
      const newData = this.tableDataList.filter(
        (data) =>
          !this.search ||
          data.title.toLowerCase().includes(this.search.toLowerCase())
      );
      this.tableData = genTree(newData)
    },
    handleAdd() {
      this.tableData = Object.assign({}, defaultM)
      this.dialogType = "new"
      this.dialogVisible = true
      this.$nextTick(() => {
        this.$refs["Form"].clearValidate()
      })
    },
    handleEdit(scope) {
      this.tableData = Object.assign({}, scope.row) // copy obj
      this.dialogType = "edit";
      this.dialogVisible = true;
      this.$nextTick(() => {
        this.$refs["Form"].clearValidate();
      })
    },
    handleDelete(scope) {
      this.$confirm("确认删除?", "警告", {
        confirmButtonText: "确认",
        cancelButtonText: "取消",
        type: "error"
      })
        .then(async() => {
          await deleteMaterial(scope.row.id);
          this.getList()
          this.$message({
            type: "success",
            message: "删除成功!"
          })
        })
        .catch((err) => {
          console.error(err)
        })
    },
    async confirm(form) {
      this.$refs[form].validate((valid) => {
        if (valid) {
          const isEdit = this.dialogType === "edit"
          if (isEdit) {
            updateMaterial(this.tableData.id, this.tableData).then(() => {
              this.getList()
              this.dialogVisible = false;
              this.$message({
                message: "编辑成功",
                type: "success"
              })
            })
          } else {
            createMaterial(this.tableData).then((res) => {
              this.getList()
              this.dialogVisible = false
              this.$message({
                message: "新增成功",
                type: "success"
              })
            })
          }
        } else {
          return false
        }
      })
    }
  }
}
</script>
<style scoped>
.avatar-uploader .el-upload:hover {
  border-color: #409eff;
}
.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 100px;
  height: 100px;
  line-height: 100px;
  text-align: center;
}
.avatar {
  width: 100px;
  height: 100px;
  display: block;
}
</style>
