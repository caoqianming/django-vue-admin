import Schema from 'async-validator'
import Organization from '@/views/system/organization.vue'
import { createOrg, updateOrg } from '@/api/org'

jest.mock('@riophae/vue-treeselect/dist/vue-treeselect.css', () => ({}))

jest.mock('@/api/org', () => ({
  getOrgAll: jest.fn(),
  createOrg: jest.fn(() => Promise.resolve({})),
  updateOrg: jest.fn(() => Promise.resolve({})),
  deleteOrg: jest.fn()
}))

describe('Organization form', () => {
  beforeEach(() => jest.clearAllMocks())

  function submit(org, dialogType = 'new') {
    const state = Organization.data()
    const schema = new Schema(state.rule1)
    const context = {
      ...state, org, dialogType,
      $refs: { Form: { validate: callback => schema.validate(org, errors => callback(!errors)) } },
      getList: jest.fn(),
      $message: jest.fn()
    }
    return Organization.methods.confirmOrg.call(context, 'Form')
  }

  it('submits the first root department without a parent', async() => {
    await submit({ name: 'Root', parent: null })
    expect(createOrg).toHaveBeenCalledWith({ name: 'Root', parent: null })
  })

  it('preserves the selected parent for a child', async() => {
    await submit({ name: 'Child', parent: 1 })
    expect(createOrg).toHaveBeenCalledWith({ name: 'Child', parent: 1 })
  })

  it('sends null when clearing an existing parent', async() => {
    await submit({ id: 2, name: 'Root', parent: undefined }, 'edit')
    expect(updateOrg).toHaveBeenCalledWith(2, { id: 2, name: 'Root', parent: null })
  })

  it('still rejects a missing name', async() => {
    await submit({ name: '', parent: null })
    expect(createOrg).not.toHaveBeenCalled()
  })
})
