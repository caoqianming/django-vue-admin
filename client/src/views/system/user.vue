<template>
  <div class="app-container">
    <el-row :gutter="10">
      <el-col :span="6">
        <el-input v-model="filterOrgText" placeholder="输入部门名进行过滤" />

        <el-tree
          ref="tree"
          v-loading="treeLoding"
          class="filter-tree"
          :data="orgData"
          default-expand-all
          highlight-current
          :expand-on-click-node="false"
          :filter-node-method="filterNode"
          style="margin-top:10px;"
          @node-click="handleOrgClick"
        />
      </el-col>
      <el-col :span="18">
        <div>
          <el-select
            v-model="listQuery.is_active"
            placeholder="状态"
            clearable
            style="width: 90px"
            class="filter-item"
            @change="handleFilter"
          >
            <el-option
              v-for="item in enabledOptions"
              :key="item.key"
              :label="item.display_name"
              :value="item.key"
            />
          </el-select>
          <el-input
            v-model="listQuery.name"
            placeholder="姓名"
            style="width: 200px;"
            class="filter-item"
            @keyup.enter.native="handleFilter"
          />
          <el-button
            class="filter-item"
            type="primary"
            icon="el-icon-search"
            @click="handleFilter"
          >搜索</el-button>
          <el-button
            class="filter-item"
            style="margin-left: 10px;"
            type="primary"
            icon="el-icon-refresh-left"
            @click="resetFilter"
          >刷新重置</el-button>
        </div>
        <div style="margin-top:10px">
          <el-button type="primary" icon="el-icon-plus" @click="handleAddUser">新增</el-button>
        </div>
        <el-table
          v-loading="listLoading"
          :data="userList.results"
          style="width: 100%;margin-top:10px;"
          border
          fit
          stripe
          highlight-current-row
          max-height="600"
        >
          <el-table-column type="index" width="50" />
          <el-table-column align="center" label="姓名">
            <template slot-scope="scope">{{ scope.row.name }}</template>
          </el-table-column>
          <el-table-column align="header-center" label="账户">
            <template slot-scope="scope">{{ scope.row.username }}</template>
          </el-table-column>
          <el-table-column align="header-center" label="部门">
            <template
              v-if="scope.row.dept_name != null"
              slot-scope="scope"
            >{{ scope.row.dept_name }}</template>
          </el-table-column>
          <!-- <el-table-column align="header-center" label="状态">
            <template slot-scope="scope">
              <el-switch
                v-model="scope.row.is_active"
                :disabled="!checkPermission(['user_update'])"
                active-color="#409EFF"
                inactive-color="#F56C6C"
              />
            </template>
          </el-table-column>-->
          <el-table-column label="创建日期">
            <template slot-scope="scope">
              <span>{{ scope.row.date_joined }}</span>
            </template>
          </el-table-column>
          <el-table-column align="center" label="操作">
            <template slot-scope="scope">
              <el-button
                v-if="!scope.row.is_superuser"
                :disabled="!checkPermission(['user_update'])"
                type="primary"
                size="small"
                icon="el-icon-edit"
                @click="handleEdit(scope)"
              />
              <el-button
                v-if="!scope.row.is_superuser"
                :disabled="!checkPermission(['user_delete'])"
                type="danger"
                size="small"
                icon="el-icon-delete"
                @click="handleDelete(scope)"
              />
            </template>
          </el-table-column>
        </el-table>

        <pagination
          v-show="userList.count>0"
          :total="userList.count"
          :page.sync="listQuery.page"
          :limit.sync="listQuery.page_size"
          @pagination="getList"
        />
      </el-col>
    </el-row>

    <el-dialog :visible.sync="dialogVisible" :title="dialogType==='edit'?'编辑用户':'新增用户'">
      <el-form ref="Form" :model="user" label-width="80px" label-position="right" :rules="rule1">
        <el-form-item label="姓名" prop="name">
          <el-input v-model="user.name" placeholder="姓名" />
        </el-form-item>
        <el-form-item label="账户" prop="username">
          <el-input v-model="user.username" placeholder="账户" />
        </el-form-item>
        <el-form-item label="所属部门" prop="dept">
          <treeselect v-model="user.dept" :multiple="false" :options="orgData" placeholder="所属部门"/>
        </el-form-item>
        <el-form-item label="角色" prop="roles">
          <el-select v-model="user.roles" multiple placeholder="请选择" style="width:100%">
            <el-option
              v-for="item in roles"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="头像" prop="dept">
          <el-upload
            class="avatar-uploader"
            :action="uploadUrl"
            accept="image/jpeg, image/gif, image/png, image/bmp"
            :show-file-list="false"
            :on-success="handleAvatarSuccess"
            :before-upload="beforeAvatarUpload"
            :headers="myHeaders"
          >
            <img v-if="user.avatar" :src="user.avatar" class="avatar" />
            <i v-else class="el-icon-plus avatar-uploader-icon" />
          </el-upload>
        </el-form-item>
      </el-form>
      <div style="text-align:right;">
        <el-button type="danger" @click="dialogVisible=false">取消</el-button>
        <el-button type="primary" @click="confirm('Form')">确认</el-button>
      </div>
    </el-dialog>
  </div>
</template>
<style>
.avatar-uploader .el-upload {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
}
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
<script>
import { getUserList, createUser, deleteUser, updateUser } from "@/api/user";
import { getOrgAll } from "@/api/org";
import { getRoleAll } from "@/api/role";
import { genTree } from "@/utils";
import checkPermission from "@/utils/permission";
import { uploadUrl } from "@/api/file";
import { getToken } from "@/utils/auth";
import Pagination from "@/components/Pagination"; // secondary package based on el-pagination
import Treeselect from '@riophae/vue-treeselect'
import '@riophae/vue-treeselect/dist/vue-treeselect.css'
const defaultUser = {
  id: "",
  name: "",
  username: "",
  dept: null,
  avatar: "/media/default/avatar.png"
};
export default {
  components: { Pagination, Treeselect },
  data() {
    return {
      user: {
        id: "",
        name: "",
        username: "",
        dept: null,
        avatar: ""
      },
      myHeaders: { Authorization: "JWT " + getToken() },
      uploadUrl: uploadUrl(),
      userList: {'count':0},
      roles: [],
      listLoading: true,
      listQuery: {
        page: 1,
        page_size: 20
      },
      enabledOptions: [
        { key: "true", display_name: "激活" },
        { key: "false", display_name: "禁用" }
      ],
      dialogVisible: false,
      dialogType: "new",
      rule1: {
        name: [{ required: true, message: "请输入姓名", trigger: "blur" }],
        username: [{ required: true, message: "请输入账号", trigger: "change" }]
        // password: [
        //   { required: true, message: '请输入密码', trigger: 'change' }
        // ],
      },
      filterOrgText: "",
      treeLoding: false,
      orgData: []
    };
  },
  computed: {},
  watch: {
    filterOrgText(val) {
      this.$refs.tree.filter(val);
    }
  },
  created() {
    this.getList();
    this.getOrgAll();
    this.getRoleAll();
  },
  methods: {
    checkPermission,
    handleAvatarSuccess(res, file) {
      if (res.code === 200) {
        this.user.avatar = res.data.path;
      } else {
        this.$message.error("头像上传失败!");
      }
    },
    beforeAvatarUpload(file) {
      const isLt2M = file.size / 1024 / 1024 < 2;
      if (!isLt2M) {
        this.$message.error("上传头像图片大小不能超过 2MB!");
      }
      return isLt2M;
    },
    filterNode(value, data) {
      if (!value) return true;
      return data.label.indexOf(value) !== -1;
    },
    handleOrgClick(obj, node, vue) {
      this.listQuery.page = 1;
      this.listQuery.dept = obj.id;
      this.getList();
    },
    getList() {
      this.listLoading = true;
      getUserList(this.listQuery).then(response => {
        if (response.data) {
          this.userList = response.data
        }
        this.listLoading = false;
      });
    },
    getOrgAll() {
      this.treeLoding = true;
      getOrgAll().then(response => {
        this.orgData = genTree(response.data);
        this.treeLoding = false;
      });
    },
    getRoleAll() {
      getRoleAll().then(response => {
        this.roles = genTree(response.data);
      });
    },
    resetFilter() {
      this.listQuery = {
        page: 1,
        page_size: 20
      };
      this.getList();
    },
    handleFilter() {
      this.listQuery.page = 1;
      this.getList();
    },
    handleAddUser() {
      this.user = Object.assign({}, defaultUser);
      this.dialogType = "new";
      this.dialogVisible = true;
      this.$nextTick(() => {
        this.$refs["Form"].clearValidate();
      });
    },
    handleEdit(scope) {
      this.user = Object.assign({}, scope.row); // copy obj
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
        type: "error"
      })
        .then(async () => {
          await deleteUser(scope.row.id);
          this.userList.splice(scope.row.index, 1);
          this.$message({
            type: "success",
            message: "成功删除!"
          });
        })
        .catch(err => {
          console.error(err);
        });
    },
    async confirm(form) {
      this.$refs[form].validate(valid => {
        if (valid) {
          const isEdit = this.dialogType === "edit";
          if (isEdit) {
            updateUser(this.user.id, this.user).then(res => {
              if (res.code >= 200) {
                this.getList();
                this.dialogVisible = false;
                this.$notify({
                  title: "成功",
                  message: "编辑成功",
                  type: "success",
                  duration: 2000
                });
              }
            });
          } else {
            createUser(this.user).then(res => {
              if (res.code >= 200) {
                this.getList();
                this.dialogVisible = false;
                this.$notify({
                  title: "成功",
                  message: "新增成功",
                  type: "success",
                  duration: 2000
                });
              }
            });
          }
        } else {
          return false;
        }
      });
    }
  }
};
</script>
