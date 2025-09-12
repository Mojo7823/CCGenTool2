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
  border-radius: 4px;
}

.node-content:hover {
  background: rgba(55, 65, 81, 0.5);
}

.expand-icon {
  width: 16px;
  margin-right: 4px;
  color: var(--muted);
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
  color: var(--text);
}

.node-data {
  color: var(--muted);
  font-style: italic;
  word-break: break-word;
  flex: 1;
}

/* Node type styling - adapted for dark theme */
.node-class {
  color: #ef4444;
  font-weight: bold;
}

.node-family {
  color: #3b82f6;
  font-weight: 600;
}

.node-component {
  color: #10b981;
  font-weight: 600;
}

.node-element {
  color: #f59e0b;
}

.node-eal {
  color: #a855f7;
  font-weight: 600;
}

.node-text {
  color: var(--text);
  font-weight: normal;
  font-size: 0.9rem;
}

.node-default {
  color: var(--muted);
}

.children {
  border-left: 1px dotted #374151;
  margin-left: 8px;
}
</style>