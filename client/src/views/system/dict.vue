<template>
  <div class="app-container">
    <el-row :gutter="10">
      <el-col :md="6">
        <el-card>
          <div slot="header" class="clearfix">
    <span>字典类型</span>
    <el-button v-if="checkPermission(['dicttype_add'])" style="float: right; padding: 3px 0" type="text" icon="el-icon-plus" @click="handleAddDictType" >新增</el-button>
  </div>
        
        <el-tree
          ref="tree"
          v-loading="treeLoding"
          class="filter-tree"
          :data="dictTypeData"
          highlight-current
          :expand-on-click-node="false"
          :filter-node-method="filterNode"
          style="margin-top:10px;"
          @node-click="handleDictTypeClick"
        >
        <span class="custom-tree-node" slot-scope="{ node, data }">
        <span>{{ node.label }}</span>
        <span>
          <el-button
            type="text"
            size="mini"
            v-if="checkPermission(['dicttype_delete'])"
            @click="handleEditDictType(data)">
            编辑
          </el-button>
          <!-- <el-button
            type="text"
            size="mini"
            @click="handleDeleteDictType">
            删除
          </el-button> -->
        </span>
      </span>
        </el-tree>
        </el-card>
      </el-col>
      <el-col :md="18">
        <el-card>
          <div slot="header" class="clearfix">
    <span>字典详情</span>
  </div>
  <div >
    <el-button v-show="listQuery.type" type="primary" icon="el-icon-plus" @click="handleAddDict" v-if="checkPermission(['dic_create'])" size="small">新增</el-button>
  </div>
        <el-table
          v-show="listQuery.type"
          v-loading="listLoading"
          :data="dictList"
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
          <el-table-column label="代号/编号">
            <template slot-scope="scope">{{ scope.row.code }}</template>
          </el-table-column>
          <el-table-column label="名称">
            <template slot-scope="scope">{{ scope.row.name }}</template>
          </el-table-column>
          <el-table-column label="描述">
            <template slot-scope="scope">{{ scope.row.description }}</template>
          </el-table-column>
          <el-table-column label="是否有效">
            <template slot-scope="scope">
              
              <el-tag type="success" v-if="scope.row.is_used">有效</el-tag>
              <el-tag type="danger" v-else>无效</el-tag>
              </template>
          </el-table-column>
          <el-table-column label="操作">
            <template slot-scope="scope">
              <el-button
                v-if="!scope.row.is_superuser"
                :disabled="!checkPermission(['dict_update'])"
                type="primary"
                size="small"
                icon="el-icon-edit"
                @click="handleEdit(scope)"
                
              />
              <!-- <el-button
                v-if="!scope.row.is_superuser"
                :disabled="!checkPermission(['dict_delete'])"
                type="danger"
                size="small"
                icon="el-icon-delete"
                @click="handleDelete(scope)"
              /> -->
            </template>
          </el-table-column>
        </el-table>
        <p v-show="!listQuery.type">点击左侧类型查看字典</p>
        <!-- <pagination
          v-show="dictList.count>0"
          :total="dictList.count"
          :page.sync="listQuery.page"
          :limit.sync="listQuery.page_size"
          @pagination="getList"
        /> -->
        </el-card>
      </el-col>
    </el-row>

    <el-dialog :visible.sync="dgV1" :title="dgT1==='edit'?'编辑字典类型':'新建字典类型'">
      <el-form ref="Form1" :model="dicttype" label-width="80px" label-position="right" :rules="rule1">
        <el-form-item label="名称" prop="name">
          <el-input v-model="dicttype.name" placeholder="名称" />
        </el-form-item>
        <el-form-item label="代号" prop="code">
          <el-input v-model="dicttype.code" placeholder="代号" />
        </el-form-item>
        <el-form-item label="父级" prop="parent">
          <treeselect v-model="dicttype.parent" :multiple="false" :options="dictTypeData" placeholder="父级"/>
        </el-form-item>
      </el-form>
      <span slot="footer">
        <el-button type="danger" @click="dgV1=false">取消</el-button>
        <el-button type="primary" @click="confirm1('Form1')">确认</el-button>
      </span>
    </el-dialog>
    <el-dialog :visible.sync="dgV2" :title="dgT2==='edit'?'编辑字典':'新建字典'">
      <el-form ref="Form2" :model="dict" label-width="80px" label-position="right" :rules="rule2">

        <el-form-item label="编号" prop="code">
          <el-input v-model="dict.code" placeholder="编号" />
        </el-form-item>
        <el-form-item label="名称" prop="name">
          <el-input type="textarea" v-model="dict.name" placeholder="名称" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input type="textarea" v-model="dict.description" placeholder="描述" />
        </el-form-item>
        <el-form-item label="父级" prop="parent">
          <treeselect v-model="dict.parent" :multiple="false" :options="dictList" placeholder="父级"/>
        </el-form-item>
        <el-form-item label="排序" prop="sort">
          <el-input-number v-model="dict.sort" :min="1" :max="999"></el-input-number>
        </el-form-item>
        <el-form-item label="是否有效" prop="is_used">
          <el-switch
  v-model="dict.is_used">
</el-switch>
        </el-form-item>
      </el-form>
      <span slot="footer">
        <el-button type="danger" @click="dgV2=false">取消</el-button>
        <el-button type="primary" @click="confirm2('Form2')">确认</el-button>
      </span>
    </el-dialog>
  </div>
</template>
<style>
  .custom-tree-node {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-size: 14px;
    padding-right: 8px;
  }
</style>
<script>
import { getDictTypeList, getDictList, createDictType, createDict, updateDictType, updateDict, deleteDictType, deleteDict } from '@/api/dict'
import { genTree } from '@/utils'
import checkPermission from '@/utils/permission'
import Pagination from '@/components/Pagination' // secondary package based on el-pagination
import Treeselect from '@riophae/vue-treeselect'
import '@riophae/vue-treeselect/dist/vue-treeselect.css'

const defaultDictType = {
  id: '',
  name: '',
  code: '',
  parent: null
}
const defaultDict = {
  id: '',
  name: '',
  description: '',
  sort: 1,
  type: null,
  is_used: true,
  parent:null
}
export default {
  components: { Pagination, Treeselect },
  data() {
    return {
      dicttype: Object.assign({}, defaultDictType),
      dict: Object.assign({}, defaultDict),
      search:'',
      dictList: [],
      listLoading: true,
      listQuery: {},
      dgV1: false,
      dgT1: 'new',
      rule1: {
        name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
        code: [{ required: true, message: '请输入代号', trigger: 'change' }]
      },
      dgV2: false,
      dgT2: 'new',
      rule2: {
        name: [{ required: true, message: '请输入名称', trigger: 'blur' }]
      },
      filterDictTypeText: '',
      treeLoding: false,
      dictTypeData: [],
    }
  },
  computed: {},
  watch: {
    filterDictTypeText(val) {
      this.$refs.tree.filter(val)
    }
  },
  created() {
    this.getDictTypeList()
  },
  methods: {
    checkPermission,
    filterNode(value, data) {
      if (!value) return true
      return data.label.indexOf(value) !== -1
    },
    handleDictTypeClick(obj, node, vue) {
      this.listQuery.type = obj.id
      this.getList()
    },
    getList() {
      this.listLoading = true
      getDictList(this.listQuery).then(response => {
          if (response.data) {
            this.dictList = genTree(response.data)
          this.listLoading = false
          }
      }).catch(error=>{this.listLoading = false})
    },
    getDictTypeList() {
      this.treeLoding = true
      getDictTypeList().then(response => {
        this.dictTypeData = genTree(response.data)
        this.treeLoding = false
      })
    },
    handleAddDictType() {
      this.dicttype = Object.assign({}, defaultDictType)
      this.dgT1 = 'new'
      this.dgV1 = true
      this.$nextTick(() => {
        this.$refs['Form1'].clearValidate()
      })
    },
    handleAddDict() {
      this.dict = Object.assign({}, defaultDict)
      this.dict.type = this.listQuery.type
      this.dgT2 = 'new'
      this.dgV2 = true
      this.$nextTick(() => {
        this.$refs['Form2'].clearValidate()
      })
    },
    handleEdit(scope) {
      this.dict = Object.assign({}, scope.row) // copy obj
      this.dgT2 = 'edit'
      this.dgV2 = true
      this.$nextTick(() => {
        this.$refs['Form2'].clearValidate()
      })
    },
    handleEditDictType(data) {
      this.dicttype = Object.assign({}, data) // copy obj
      this.dgT1 = 'edit'
      this.dgV1 = true
      this.$nextTick(() => {
        this.$refs['Form1'].clearValidate()
      })

    },
    handleDelete(scope) {
      this.$confirm('确认删除?', '警告', {
        confirmButtonText: '确认',
        cancelButtonText: '取消',
        type: 'error'
      })
        .then(async() => {
          const { code } = await deleteDict(scope.row.id)
          if (code>=200){
          this.dictList.splice(scope.row.index, 1)
          this.$message({
            type: 'success',
            message: '成功删除!'
          })
          }
        })
        .catch(err => {
          console.error(err)
        })
    },
    async confirm1(form) {
      this.$refs[form].validate(valid => {
        if (valid) {
          const isEdit = this.dgT1 === 'edit'
          if (isEdit) {
            updateDictType(this.dicttype.id, this.dicttype).then(res => {
                this.getDictTypeList()
                this.dgV1 = false
                this.$message({
                  message: '编辑成功',
                  type: 'success',
                })
            }).catch(error=>{})
          } else {
            createDictType(this.dicttype).then(res => {
                this.getDictTypeList()
                this.dgV1 = false
                this.$message({
                  message: '新增成功',
                  type: 'success',
                })
            }).catch(error=>{})
          }
        } else {
          return false
        }
      })
    },
    async confirm2(form) {
      this.$refs[form].validate(valid => {
        if (valid) {
          const isEdit = this.dgT2 === 'edit'
          if (isEdit) {
            updateDict(this.dict.id, this.dict).then(res => {
                this.getList()
                this.dgV2 = false
                this.$message({
                  message: '编辑成功',
                  type: 'success',
                })
            }).catch(error=>{})
          } else {
            createDict(this.dict).then(res => {
                this.getList()
                this.dgV2 = false
                this.$message({
                  message: '新增成功',
                  type: 'success',
                })
            }).catch(error=>{})
          }
        } else {
          return false
        }
      })
    }
  }
}
</script>
