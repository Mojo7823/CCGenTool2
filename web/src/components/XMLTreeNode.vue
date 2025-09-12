<template>
  <div class="tree-node">
    <div 
      class="node-content"
      :style="{ marginLeft: `${level * 20}px` }"
      @click="toggleExpanded"
    >
      <span v-if="node.children && node.children.length > 0" class="expand-icon">
        {{ isExpanded ? '▼' : '▶' }}
      </span>
      <span v-else class="expand-icon-placeholder"></span>
      
      <span class="node-label" :class="getNodeClass()">
        {{ node.label }}
      </span>
      
      <span v-if="node.data" class="node-data">
        : {{ node.data }}
      </span>
    </div>

    <div v-if="isExpanded && node.children && node.children.length > 0" class="children">
      <XMLTreeNode
        v-for="(child, index) in node.children"
        :key="index"
        :node="child"
        :level="level + 1"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

interface TreeNode {
  label: string
  data?: string | null
  attributes: Record<string, string>
  children: TreeNode[]
}

interface Props {
  node: TreeNode
  level: number
}

const props = defineProps<Props>()

const isExpanded = ref(true) // Start expanded by default for first few levels

function toggleExpanded() {
  if (props.node.children && props.node.children.length > 0) {
    isExpanded.value = !isExpanded.value
  }
}

function getNodeClass() {
  const label = props.node.label.toLowerCase()
  
  if (label.includes('f-class') || label.includes('a-class')) {
    return 'node-class'
  } else if (label.includes('f-family') || label.includes('a-family')) {
    return 'node-family'
  } else if (label.includes('f-component') || label.includes('a-component')) {
    return 'node-component'
  } else if (label.includes('f-element') || label.includes('a-element')) {
    return 'node-element'
  } else if (label.includes('eal')) {
    return 'node-eal'
  } else if (props.node.children.length === 0 && props.node.label.length > 50) {
    return 'node-text'
  }
  
  return 'node-default'
}
</script>

<style scoped>
.tree-node {
  user-select: none;
}

.node-content {
  display: flex;
  align-items: flex-start;
  padding: 2px 0;
  cursor: pointer;
  word-wrap: break-word;
}

.node-content:hover {
  background-color: #f0f0f0;
}

.expand-icon {
  width: 16px;
  margin-right: 4px;
  color: #666;
  font-size: 12px;
  flex-shrink: 0;
}

.expand-icon-placeholder {
  width: 16px;
  margin-right: 4px;
  flex-shrink: 0;
}

.node-label {
  font-weight: 500;
  margin-right: 8px;
  word-break: break-word;
}

.node-data {
  color: #666;
  font-style: italic;
  word-break: break-word;
  flex: 1;
}

/* Node type styling */
.node-class {
  color: #d73502;
  font-weight: bold;
}

.node-family {
  color: #0066cc;
  font-weight: 600;
}

.node-component {
  color: #006600;
  font-weight: 600;
}

.node-element {
  color: #cc6600;
}

.node-eal {
  color: #9900cc;
  font-weight: 600;
}

.node-text {
  color: #333;
  font-weight: normal;
  font-size: 0.9rem;
}

.node-default {
  color: #555;
}

.children {
  border-left: 1px dotted #ccc;
  margin-left: 8px;
}
</style>