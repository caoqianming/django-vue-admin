<template>
  <div class="app-container">
    <div>
      <el-input
        v-model="search"
        placeholder="输入课程名称进行搜索"
        style="width: 200px"
        class="filter-item"
        @keyup.native="resetFilter"
      />
      <el-button
        type="primary"
        icon="el-icon-plus"
        @click="handleAdd"
        v-if="checkPermission(['position_create'])"
        size="small"
      >新增
      </el-button
      >
    </div>
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
      <el-table-column type="index" width="50"/>
      <el-table-column label="课程名称">
        <template slot-scope="scope">{{ scope.row.title }}</template>
      </el-table-column>
      <el-table-column label="课程类型">
        <template slot-scope="scope">{{ scope.row.type }}</template>
      </el-table-column>
      <el-table-column label="课程数量">
        <template slot-scope="scope">{{ scope.row.lesson_count }}</template>
      </el-table-column>
      <el-table-column label="课程描述">
        <template slot-scope="scope">{{ scope.row.description }}</template>
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
      :title="dialogType === 'edit' ? '编辑课程' : '新增课程'"
    >
      <el-form
        ref="Form"
        :model="tableData"
        label-width="80px"
        label-position="right"
      >
        <el-form-item label="课程名称" prop="title">
          <el-input v-model="tableData.title" placeholder="课程名称"/>
        </el-form-item>
        <el-form-item label="课程类型" prop="type">
          <el-select
                v-model="tableData.type"
                placeholder="请选择"
                style="width: 90%"
              >
                <el-option
                  v-for="item in dataOptions"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
                />
              </el-select>
        </el-form-item>
        <el-form-item label="课时数量" prop="lesson_count">
          <el-input-number v-model="tableData.lesson_count" placeholder="课时数量"/>
        </el-form-item>
        <el-form-item label="课程描述" prop="description">
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
  getCourseById,
  getCourseList,
  createCourse,
  updateCourse,
  deleteCourse
} from "@/api/course";
import {genTree, deepClone} from "@/utils";
import checkPermission from "@/utils/permission";

const defaultM = {
  title: "",
  type: "",
  description: ""
};
export default {
  data() {
    return {
      tableData: {
        id: "",
        title: "",
        type: "",
        description: "",
        create_time: "",
        update_time: ""
      },
      search: "",
      tableDataList: [],
      listLoading: true,
      dialogVisible: false,
      dialogType: "new",
      dataOptions: [
        {
          value: "公开课",
          label: "公开课",
        },
        {
          value: "入门课",
          label: "入门课",
        },
        {
          value: "进阶课",
          label: "进阶课",
        }
      ],
    };
  },
  computed: {},
  created() {
    this.getList();
  },
  methods: {
    checkPermission,
    getList() {
      this.listLoading = true;
      getCourseList(this.search).then((response) => {
        this.tableDataList = response.data;
        this.tableData = response.data;
        this.listLoading = false;
      });
    },
    resetFilter() {
      this.getList();
    },
    handleFilter() {
      const newData = this.tableDataList.filter(
        (data) =>
          !this.search ||
          data.title.toLowerCase().includes(this.search.toLowerCase())
      );
      this.tableData = genTree(newData);
    },
    handleAdd() {
      this.tableData = Object.assign({}, defaultM);
      this.dialogType = "new";
      this.dialogVisible = true;
      this.$nextTick(() => {
        this.$refs["Form"].clearValidate();
      });
    },
    handleEdit(scope) {
      this.tableData = Object.assign({}, scope.row); // copy obj
      this.dialogType = "edit";
      this.dialogVisible = true;
      this.$nextTick(() => {
        this.$refs["Form"].clearValidate();
      });
    },
    handleDelete(scope) {
      this.$confirm("确认删除?", "警告", {
        confirmButtonText: "确认",
        cancelButtonText: "取消",
        type: "error",
      })
        .then(async () => {
          await deleteCourse(scope.row.id);
          this.getList();
          this.$message({
            type: "success",
            message: "成功删除!",
          });
        })
        .catch((err) => {
          console.error(err);
        });
    },
    async confirm(form) {
      this.$refs[form].validate((valid) => {
        if (valid) {
          const isEdit = this.dialogType === "edit";
          if (isEdit) {
            updateCourse(this.tableData.id, this.tableData).then(() => {
              this.getList();
              this.dialogVisible = false;
              this.$message({
                message: "编辑成功",
                type: "success",
              });
            });
          } else {
            createCourse(this.tableData).then((res) => {
              this.getList();
              this.dialogVisible = false;
              this.$message({
                message: "新增成功",
                type: "success",
              });
            });
          }
        } else {
          return false;
        }
      });
    },
  },
};
</script>
