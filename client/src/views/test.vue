<template>
  <div>
    <el-form ref="elForm" :model="formData" :rules="rules" size="medium" label-width="100px">
      <el-form-item label="单行文本" prop="mobile">
        <el-input v-model="formData.mobile" placeholder="请输入手机号" :maxlength="11" show-word-limit clearable
                  prefix-icon='el-icon-mobile' :style="{width: '100%'}"></el-input>
      </el-form-item>
      <el-form-item label="单行文本" prop="field101">
        <el-input v-model="formData.field101" placeholder="请输入单行文本" clearable :style="{width: '100%'}">
        </el-input>
      </el-form-item>
      <el-form-item label="多行文本" prop="field102">
        <el-input v-model="formData.field102" type="textarea" placeholder="请输入多行文本"
                  :autosize="{minRows: 4, maxRows: 4}" :style="{width: '100%'}"></el-input>
      </el-form-item>
      <el-form-item label="密码" prop="field103">
        <el-input v-model="formData.field103" placeholder="请输入密码" clearable show-password
                  :style="{width: '100%'}"></el-input>
      </el-form-item>
      <el-form-item label="计数器" prop="field104">
        <el-input-number v-model="formData.field104" placeholder="计数器" :step='1'></el-input-number>
      </el-form-item>
      <el-form-item label="下拉选择" prop="field105">
        <el-select v-model="formData.field105" placeholder="请选择下拉选择" clearable :style="{width: '100%'}">
          <el-option v-for="(item, index) in field105Options" :key="index" :label="item.label"
                     :value="item.value" :disabled="item.disabled"></el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="多选框组" prop="field106">
        <el-checkbox-group v-model="formData.field106" size="medium">
          <el-checkbox v-for="(item, index) in field106Options" :key="index" :label="item.value"
                       :disabled="item.disabled">{{item.label}}</el-checkbox>
        </el-checkbox-group>
      </el-form-item>
      <el-form-item label="日期范围" prop="field107">
        <el-date-picker type="daterange" v-model="formData.field107" format="yyyy-MM-dd"
                        value-format="yyyy-MM-dd" :style="{width: '100%'}" start-placeholder="开始日期" end-placeholder="结束日期"
                        range-separator="至" clearable></el-date-picker>
      </el-form-item>
      <el-form-item label="日期选择" prop="field108">
        <el-date-picker v-model="formData.field108" format="yyyy-MM-dd" value-format="yyyy-MM-dd"
                        :style="{width: '100%'}" placeholder="请选择日期选择" clearable></el-date-picker>
      </el-form-item>
      <el-form-item label="评分" prop="field109">
        <el-rate v-model="formData.field109" :max='5'></el-rate>
      </el-form-item>
      <el-form-item label="颜色选择" prop="field110" required>
        <el-color-picker v-model="formData.field110" size="medium"></el-color-picker>
      </el-form-item>
      <el-form-item label="编辑器" prop="field111">
        <tinymce v-model="formData.field111" placeholder="请输入编辑器" :height="300"></tinymce>
      </el-form-item>
      <el-form-item size="large">
        <el-button type="primary" @click="submitForm">提交</el-button>
        <el-button @click="resetForm">重置</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>
<script>
export default {
  components: {},
  props: [],
  data() {
    return {
      formData: {
        mobile: undefined,
        field101: undefined,
        field102: undefined,
        field103: undefined,
        field104: undefined,
        field105: undefined,
        field106: [],
        field107: null,
        field108: null,
        field109: 0,
        field110: null,
        field111: null,
      },
      rules: {
        mobile: [{
          required: true,
          message: '请输入手机号',
          trigger: 'blur'
        }, {
          pattern: /^1(3|4|5|7|8|9)\d{9}$/,
          message: '手机号格式错误',
          trigger: 'blur'
        }],
        field101: [{
          required: true,
          message: '请输入单行文本',
          trigger: 'blur'
        }],
        field102: [{
          required: true,
          message: '请输入多行文本',
          trigger: 'blur'
        }],
        field103: [{
          required: true,
          message: '请输入密码',
          trigger: 'blur'
        }],
        field104: [{
          required: true,
          message: '计数器',
          trigger: 'blur'
        }],
        field105: [{
          required: true,
          message: '请选择下拉选择',
          trigger: 'change'
        }],
        field106: [{
          required: true,
          type: 'array',
          message: '请至少选择一个多选框组',
          trigger: 'change'
        }],
        field107: [{
          required: true,
          message: '日期范围不能为空',
          trigger: 'change'
        }],
        field108: [{
          required: true,
          message: '请选择日期选择',
          trigger: 'change'
        }],
        field109: [{
          required: true,
          message: '评分不能为空',
          trigger: 'change'
        }],
        field111: [{
          required: true,
          message: '请输入编辑器',
          trigger: 'blur'
        }],
      },
      field105Options: [{
        "label": "选项一",
        "value": 1
      }, {
        "label": "选项二",
        "value": 2
      }],
      field106Options: [{
        "label": "选项一",
        "value": 1
      }, {
        "label": "选项二",
        "value": 2
      }],
    }
  },
  computed: {},
  watch: {},
  created() {},
  mounted() {},
  methods: {
    submitForm() {
      this.$refs['elForm'].validate(valid => {
        if (!valid) return
        // TODO 提交表单
      })
    },
    resetForm() {
      this.$refs['elForm'].resetFields()
    },
  }
}

</script>
<style>
.el-rate {
  display: inline-block;
  vertical-align: text-top;
}

</style>
