<template>
  <div class="app-container">
    <div>
      <el-input
        v-model="search"
        placeholder="输入岗位名称进行搜索"
        style="width: 200px;"
        class="filter-item"
        @keyup.native="handleFilter"
      />
      <el-button type="primary" icon="el-icon-plus" @click="handleAdd" v-if="checkPermission(['position_create'])" size="small">新增</el-button>
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
    >
      <el-table-column type="index" width="50" />
      <el-table-column label="岗位名称">
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

    <el-dialog :visible.sync="dialogVisible" :title="dialogType==='edit'?'编辑岗位':'新增岗位'">
      <el-form
        ref="Form"
        :model="position"
        label-width="80px"
        label-position="right"
        :rules="rule1"
      >
        <el-form-item label="名称" prop="name">
          <el-input v-model="position.name" placeholder="名称" />
        </el-form-item>
      </el-form>
      <span slot="footer">
        <el-button type="danger" @click="dialogVisible=false">取消</el-button>
        <el-button type="primary" @click="confirm('Form')">确认</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import {
  getPositionAll,
  createPosition,
  deletePosition,
  updatePosition
} from '@/api/position'
import { genTree, deepClone } from '@/utils'
import checkPermission from '@/utils/permission'

const defaultM = {
  id: '',
  name: ''
}
export default {
  data() {
    return {
      position: {
        id: '',
        name: ''
      },
      search: '',
      tableData: [],
      positionList: [],
      listLoading: true,
      dialogVisible: false,
      dialogType: 'new',
      rule1: {
        name: [{ required: true, message: '请输入名称', trigger: 'blur' }]
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
      getPositionAll().then(response => {
        this.positionList = response.data
        this.tableData = response.data
        this.listLoading = false
      })
    },
    resetFilter() {
      this.getList()
    },
    handleFilter() {
      const newData = this.positionList.filter(
        data =>
          !this.search ||
          data.name.toLowerCase().includes(this.search.toLowerCase())
      )
      this.tableData = genTree(newData)
    },
    handleAdd() {
      this.position = Object.assign({}, defaultM)
      this.dialogType = 'new'
      this.dialogVisible = true
      this.$nextTick(() => {
        this.$refs['Form'].clearValidate()
      })
    },
    handleEdit(scope) {
      this.position = Object.assign({}, scope.row) // copy obj
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
          await deletePosition(scope.row.id)
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
    async confirm(form) {
      this.$refs[form].validate(valid => {
        if (valid) {
          const isEdit = this.dialogType === 'edit'
          if (isEdit) {
            updatePosition(this.position.id, this.position).then(() => {
              this.getList()
              this.dialogVisible = false
              this.$message({
                message: '编辑成功',
                type: 'success',
              })
            })
          } else {
            createPosition(this.position).then(res => {
              // this.position = res.data
              // this.tableData.unshift(this.position)
              this.getList()
              this.dialogVisible = false
              this.$message({
                message: '新增成功',
                type: 'success',
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
