<template>
  <div class="app-container">
    <div>
      <el-input
        v-model="search"
        placeholder="输入权限名称进行搜索"
        style="width: 200px;"
        class="filter-item"
        @keyup.native="handleFilter"
      />
      <el-button type="primary" icon="el-icon-plus" @click="handleAdd" v-if="checkPermission(['perm_create'])">新增</el-button>
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
      :tree-props="{children: 'children', hasChildren: 'hasChildren'}"
    >
      <el-table-column label="菜单名称">
        <template slot-scope="scope">{{ scope.row.name }}</template>
      </el-table-column>
      <el-table-column label="类型">
        <template slot-scope="scope">{{ scope.row.type }}</template>
      </el-table-column>
      <el-table-column label="代号">
        <template slot-scope="scope">{{ scope.row.method }}</template>
      </el-table-column>
      <el-table-column label="排序">
        <template slot-scope="scope">{{ scope.row.sort }}</template>
      </el-table-column>
      <el-table-column align="center" label="操作">
        <template slot-scope="scope">
          <el-button
            type="primary"
            size="small"
            icon="el-icon-edit"
            :disabled="!checkPermission(['perm_update'])"
            @click="handleEdit(scope)"
          />
          <el-button
            type="danger"
            size="small"
            icon="el-icon-delete"
            :disabled="!checkPermission(['perm_delete'])"
            @click="handleDelete(scope)"
          />
        </template>
      </el-table-column>
    </el-table>

    <el-dialog :visible.sync="dialogVisible" :title="dialogType==='edit'?'编辑':'新增'">
      <el-form ref="Form" :model="perm" label-width="80px" label-position="right" :rules="rule1">
          <el-form-item label="类型">
    <el-radio-group v-model="perm.type">
      <el-radio label="目录"></el-radio>
      <el-radio label="菜单"></el-radio>
      <el-radio label="接口"></el-radio>
    </el-radio-group>
  </el-form-item>
        <el-form-item label="名称" prop="name">
          <el-input v-model="perm.name" placeholder="名称" />
        </el-form-item>
        <el-form-item label="代号" prop="method">
          <el-input v-model="perm.method" placeholder="代号" />
        </el-form-item>
        <el-form-item label="父级" prop="parent">
          <treeselect v-model="perm.parent" :multiple="false" :options="tableData" placeholder="父级"/>
        </el-form-item>
        <el-form-item label="排序" prop="sort">
          <el-input-number v-model="perm.sort" :min="1" label="排序"></el-input-number>
        </el-form-item>
        
      </el-form>
      <span slot="footer">
        <el-button type="danger" @click="dialogVisible=false">取消</el-button>
        <el-button type="primary" @click="confirmPerm('Form')">确认</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import { getPermAll, createPerm, deletePerm, updatePerm } from '@/api/perm'
import { genTree } from '@/utils'
import checkPermission from '@/utils/permission'
import Treeselect from '@riophae/vue-treeselect'
import '@riophae/vue-treeselect/dist/vue-treeselect.css'
const defaultPerm = {
        id: null,
        name: '',
        type: '目录',
        method: '',
        sort:1,
        parent: null
      }
export default {
  components: { Treeselect },
  data() {
    return {
      perm: defaultPerm,
      search: '',
      tableData: [],
      permList: [],
      listLoading: true,
      dialogVisible: false,
      dialogType: 'new',
      rule1: {
        name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
        method: [{ required: true, message: '请输入代号', trigger: 'blur' }]
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
      getPermAll().then(response => {
        this.permList = response.data
        const data = genTree(response.data)
        this.tableData = data
        this.listLoading = false
      })
    },
    resetFilter() {
      this.getList()
    },
    handleFilter() {
      const newData = this.permList.filter(
        data =>
          !this.search ||
          data.name.toLowerCase().includes(this.search.toLowerCase())
      )
      this.tableData = genTree(newData)
    },
    handleAdd() {
      this.perm = Object.assign({}, defaultPerm)
      this.dialogType = 'new'
      this.dialogVisible = true
      this.$nextTick(() => {
        this.$refs['Form'].clearValidate()
      })
    },
    handleEdit(scope) {
      this.perm = Object.assign({}, scope.row) // copy obj
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
          await deletePerm(scope.row.id)
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
    async confirmPerm(form) {
      this.$refs[form].validate(valid => {
        if (valid) {
          const isEdit = this.dialogType === 'edit'
          if (isEdit) {
            updatePerm(this.perm.id, this.perm).then(() => {
              this.getList()
              this.dialogVisible = false
              this.$message({
                message: '编辑成功',
                type: 'success',
              })
            })
          } else {
            createPerm(this.perm).then(res => {
              // this.perm = res.data
              // this.tableData.unshift(this.perm)
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
