<template>
  <div class="app-container">
    <el-card>
      <div>
        <el-button type="primary" icon="el-icon-plus" @click="handleAdd">新增卡片</el-button>
        <el-select v-model="tableData.type" placeholder="卡片类型" style="width: 120px">
          <el-option v-for="(item, index) in typeOptions" :key="index" :label="item.label"
                     :value="item.value"></el-option>
        </el-select>
        <el-input
          v-model="tableDataList.search"
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

    <el-table
      v-loading="listLoading"
      :data="
        tableDataList.filter(
          (data) =>
            !search || data.title.toLowerCase().includes(search.toLowerCase())
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
      <el-table-column label="标题">
        <template slot-scope="scope">{{ scope.row.title }}</template>
      </el-table-column>
      <el-table-column label="类型">
        <template slot-scope="scope">{{ scope.row.type }}</template>
      </el-table-column>
      <el-table-column label="分组">
        <template slot-scope="scope">{{ scope.row.group_name }}</template>
      </el-table-column>
      <el-table-column label="难度">
        <template slot-scope="scope">{{ scope.row.difficulty }}</template>
      </el-table-column>
      <el-table-column label="话题">
        <template slot-scope="scope">{{ scope.row.topic }}</template>
      </el-table-column>
      <el-table-column label="状态">
        <template slot-scope="scope">{{ scope.row.status }}</template>
      </el-table-column>
      <el-table-column label="预览链接">
        <template slot-scope="scope">{{ scope.row.id }}</template>
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
      :title="dialogType === 'edit' ? '编辑卡片' : '新增卡片'"
    >
      <el-form
        ref="Form"
        :model="tableData"
        label-width="80px"
        label-position="right"
      >
        <el-form-item label="卡片标题" prop="title">
          <el-input v-model="tableData.title" placeholder="卡片标题"/>
        </el-form-item>
        <el-form-item label="卡片类型" prop="type">
          <el-select
            v-model="tableData.type"
            placeholder="请选择"
            style="width: 90%"
          >
            <el-option
              v-for="item in typeOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="分组" prop="group_name">
          <el-input v-model="tableData.group_name" placeholder="分组"/>
        </el-form-item>
        <el-form-item label="状态">
           <el-radio-group v-model="tableData.status">
            <el-radio label=0>下线</el-radio>
            <el-radio label=1>上线</el-radio>
           </el-radio-group>
        </el-form-item>
        <!-- todo 这里要支持图片上传，然后将相对路径赋值-> 多选 -->
        <el-form-item label="核心图" prop="card_core_image">
          <el-upload
            class="avatar-uploader"
            :action="upUrl"
            accept="image/jpeg, image/gif, image/png, image/bmp"
            :show-file-list="false"
            :on-success="handleAvatarSuccess"
            :before-upload="beforeAvatarUpload"
            :headers="upHeaders"
          >
            <img v-if="tableData.card_core_image" :src="tableData.card_core_image" class="avatar" />
            <i v-else class="el-icon-plus avatar-uploader-icon" />
          </el-upload>
        </el-form-item>
        <el-form-item label="话题" prop="topic">
          <el-input v-model="tableData.topic" placeholder="话题"/>
        </el-form-item>
        <el-form-item label="难度" prop="difficulty">
           <el-select
            v-model="tableData.difficulty"
            placeholder="请选择"
            style="width: 90%"
          >
            <el-option
              v-for="item in difficultyOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <!-- todo 这里需要支持获取素材列表，搜索-> 多选 -->
        <el-form-item label="关联素材" prop="study_materials">
          <el-input v-model="tableData.study_materials" placeholder="关联素材"/>
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="tableData.description" placeholder="课程描述" :autosize="{ minRows: 2, maxRows: 4 }"
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
  getCardById,
  getCardList,
  createCard,
  updateCard,
  deleteCard
} from "@/api/card";
import {genTree, deepClone} from "@/utils";
import checkPermission from "@/utils/permission";
import {upUrl,upHeaders} from "@/api/file";

const defaultM = {
  title: "",
  type: "",
  description: "",
  status: 0,
  card_core_image: "",
  group_name: "",
  topic: "",
  difficulty: "",
  study_materials: []
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
        status: 0,
        card_core_image: "",
        group_name: "",
        topic: "",
        difficulty: "",
        study_materials: []
      },
      search: "",
      tableDataList: [],
      listLoading: true,
      dialogVisible: false,
      dialogType: "new",
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
          "label": "单词卡",
          "value": "编程课"
        }, {
          "label": "语法卡",
          "value": "编程卡"
        }],
      listQuery: {
        page: 1,
        page_size: 20,
      },
    };
  },
  computed: {},
  created() {
    this.getList()
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
    getList() {
      this.listLoading = true;
      getCardList(this.search).then((response) => {
        this.tableDataList = response.data;
        this.tableData = response.data;
        this.listLoading = false;
      })
    },
    resetFilter() {
      this.getList()
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
          await deleteCard(scope.row.id);
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
            updateCard(this.tableData.id, this.tableData).then(() => {
              this.getList()
              this.dialogVisible = false;
              this.$message({
                message: "编辑成功",
                type: "success"
              })
            })
          } else {
            createCard(this.tableData).then((res) => {
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
