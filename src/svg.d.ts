declare module '*.svg' {
  import type Vue, {VueConstructor} from 'vue'
  const content: VueConstructor<Vue>
  export default content
}
