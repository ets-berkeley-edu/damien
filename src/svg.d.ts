declare module '*.svg' {
  import type {default as Vue, VueConstructor} from 'vue'
  const content: VueConstructor<Vue>
  export default content
}
