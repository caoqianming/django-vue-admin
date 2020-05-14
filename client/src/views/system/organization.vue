<template>
  <div class="app-container">
    <div style="margin-top:10px">
      <el-input
        v-model="search"
        placeholder="输入部门名称进行搜索"
        style="width: 200px;"
        class="filter-item"
        @keyup.native="handleFilter"
      />
      <el-button type="primary" icon="el-icon-plus" @click="handleAdd">新增</el-button>
    </div>
    <el-table
      v-loading="listLoading"
      :data="tableData.filter(data => !search || data.name.toLowerCase().includes(search.toLowerCase()))"
      style="width: 100%;margin-top:10px;"
      border
      fit
      stripe
      highlight-current-row
      max-height="600"
      row-key="id"
      default-expand-all
      :tree-props="{children: 'children', hasChildren: 'hasChildren'}"
    >
      <el-table-column type="index" width="50" />
      <el-table-column label="组织名称">
        <template slot-scope="scope">{{ scope.row.name }}</template>
      </el-table-column>
      <el-table-column label="创建日期">
        <template slot-scope="scope">
          <span>{{ scope.row.create_time }}</span>
        </template>
      </el-table-column>
      <el-table-column align="center" label="操作">
        <template slot-scope="scope">
          <el-button
            v-if="scope.row.type==='部门'"
            type="primary"
            size="small"
            icon="el-icon-edit"
            :disabled="!checkPermission(['org_update'])"
            @click="handleEdit(scope)"
          />
          <el-button
            v-if="scope.row.type==='部门'"
            type="danger"
            size="small"
            icon="el-icon-delete"
            :disabled="!checkPermission(['org_delete'])"
            @click="handleDelete(scope)"
          />
        </template>
      </el-table-column>
    </el-table>

    <el-dialog :visible.sync="dialogVisible" :title="dialogType==='edit'?'编辑部门':'新增部门'">
      <el-form ref="Form" :model="org" label-width="80px" label-position="right" :rules="rule1">
        <el-form-item label="名称" prop="name">
          <el-input v-model="org.name" placeholder="名称" />
        </el-form-item>
        <el-form-item label="上级部门" prop="pid">
          <el-cascader
            v-model="org.pid"
            :options="pidList"
            :props="{ checkStrictly: true }"
            clearable
            style="width:100%"
          />
        </el-form-item>
      </el-form>
      <div style="text-align:right;">
        <el-button type="danger" @click="dialogVisible=false">取消</el-button>
        <el-button type="primary" @click="confirmOrg('Form')">确认</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { getOrgAll, createOrg, deleteOrg, updateOrg } from '@/api/org'
import { genTree } from '@/utils'
import checkPermission from '@/utils/permission'

const defaultOrg = {
  id: '',
  name: '',
  pid: ''
}
export default {
  data() {
    return {
      org: {
        id: '',
        name: '',
        pid: ''
      },
      search: '',
      tableData: [],
      orgList: [],
      pidList: [],
      listLoading: true,
      dialogVisible: false,
      dialogType: 'new',
      rule1: {
        name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
        pid: [{ required: true, message: '请选择上级', trigger: 'change' }]
      }
    }
  },
  computed: {},
  created() {
    this.getList()
  },
  methods: {
    checkPermission,
    getList() {
      this.listLoading = true
      getOrgAll().then(response => {
        this.orgList = response.data
        const data = genTree(response.data)
        this.tableData = data
        this.pidList = data
        this.listLoading = false
      })
    },
    resetFilter() {
      this.getList()
    },
    handleFilter() {
      const newData = this.orgList.filter(
        data =>
          !this.search ||
          data.name.toLowerCase().includes(this.search.toLowerCase())
      )
      this.tableData = genTree(newData)
    },
    handleAdd() {
      this.org = Object.assign({}, defaultOrg)
      this.dialogType = 'new'
      this.dialogVisible = true
      this.$nextTick(() => {
        this.$refs['Form'].clearValidate()
      })
    },
    handleEdit(scope) {
      this.org = Object.assign({}, scope.row) // copy obj
      this.dialogType = 'edit'
      this.dialogVisible = true
      this.$nextTick(() => {
        this.$refs['Form'].clearValidate()
      })
    },
    handleDelete(scope) {
      this.$confirm('确认删除?', '警告', {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'error'
      })
        .then(async() => {
          await deleteOrg(scope.row.id)
          this.getList()
          this.$message({
            type: 'success',
            message: '成功删除!'
          })
        })
        .catch(err => {
          console.error(err)
        })
    },
    async confirmOrg(form) {
      this.$refs[form].validate(valid => {
        if (valid) {
          const isEdit = this.dialogType === 'edit'
          if (isEdit) {
            this.org.pid = this.org.pid.pop()
            updateOrg(this.org.id, this.org).then(() => {
              this.getList()
              this.dialogVisible = false
              this.$notify({
                title: '成功',
                message: '编辑成功',
                type: 'success',
                duration: 2000
              })
            })
          } else {
            this.org.pid = this.org.pid.pop()
            createOrg(this.org).then(res => {
              // this.org = res.data
              // this.tableData.unshift(this.org)
              this.getList()
              this.dialogVisible = false
              this.$notify({
                title: '成功',
                message: '新增成功',
                type: 'success',
                duration: 2000
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
