<template>
  <div class="app-container">
    <el-card>
      <div>课程
        <el-select v-model="courseId" placeholder="请选择">
          <el-option
            v-for="item in courseList"
            :key="item.id"
            :label="`【${item.id}】- ${item.title} (${item.type})`"
            :value="item.id">
            <!--            <span style="float: right; color: #8492a6; font-size: 13px">{{ item.value }}</span>-->
          </el-option>
        </el-select>
        <el-select v-model="listQuery.type"
                   placeholder="课时类型"
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
        </el-button>
        <el-button type="primary" icon="el-icon-plus" @click="handleAdd">新增课时</el-button>
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
      <el-table-column label="课时序号" width="60">
        <template slot-scope="scope">{{ scope.row.lesson_number }}</template>
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
      <el-table-column label="版本">
        <template slot-scope="scope">{{ scope.row.version }}</template>
      </el-table-column>
      <el-table-column label="描述">
        <template slot-scope="scope">{{ scope.row.description }}</template>
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
      :title="dialogType === 'edit' ? '编辑课时' : '新增课时'"
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
        <el-form-item label="课时序号" prop="lesson_number">
          <el-input v-model="tableData.lesson_number" placeholder="课时序号"/>
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

        <el-form-item label="版本" prop="version">
          <el-input v-model="tableData.version" placeholder="版本"/>
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
  getLessonById,
  getLessonList,
  createLesson,
  updateLesson,
  deleteLesson
} from "@/api/lesson";
import {getCourseList} from "@/api/course";
import {genTree, deepClone} from "@/utils";
import checkPermission from "@/utils/permission";
import {getEnumConfigList} from "@/api/enum_config";

const defaultM = {
  title: "",
  type: "",
  description: "",
  lesson_number: 1,
  group_name: "默认分组",
  version: "first",
  cards: []
};
export default {
  data() {
    return {
      courseList: [],
      courseData: {id: null},
      courseId: null,
      courseSearch: "",
      tableData: {
        id: "",
        title: "",
        type: "",
        description: "",
        lesson_number: 1,
        group_name: "默认分组",
        version: "first",
        cards: []
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
      typeOptions: [],
      listQuery: {
        page: 1,
        page_size: 20,
        search: null
      },
      enumConfigQuery: {
        module: 'lesson',
        service: 'type'
      },
      total: 0
    };
  },
  computed: {},
  created() {
      this.getLessonTypeList();
      this.getCourseData().then(() => {
        this.getList();
    });
  },
  methods: {
    checkPermission,
    changeStatus(value) {
      this.tableData.status = value;
    },
    getLessonTypeList(){
      getEnumConfigList(this.enumConfigQuery).then((response) => {
        this.typeOptions = response.data;
      })
    },
    handleCourseChange() {
      this.listQuery.course_id = this.courseData.id;
    },
    getCourseData() {
      return new Promise((resolve, reject) => {
        getCourseList(this.courseSearch).then((response) => {
          this.courseList = response.data;
          if (this.courseList && this.courseList.length > 0) {
            this.courseId = this.courseList[0].id;
          }
          resolve();
        });
      });
    },

    getList() {
      this.listLoading = true;
      this.listQuery.course_id = this.courseId;
      getLessonList(this.listQuery).then((response) => {
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
          !this.listQuery.search ||
          data.title.toLowerCase().includes(this.listQuery.search.toLowerCase())
      );
      this.tableData = genTree(newData);
    },
    handleAdd() {
      this.tableData = Object.assign({}, defaultM);
      this.dialogType = "new";
      this.dialogVisible = true;
      this.tableData.course_id = this.courseId;
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
          await deleteLesson(scope.row.id);
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
            updateLesson(this.tableData.id, this.tableData).then(() => {
              this.getList();
              this.dialogVisible = false;
              this.$message({
                message: "编辑成功",
                type: "success",
              });
            });
          } else {
            createLesson(this.tableData).then((res) => {
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
  watch: {
}
};
</script>
