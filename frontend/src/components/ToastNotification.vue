<template>
  <transition name="toast">
    <div v-if="visible" :class="['toast-notification', type]">
      <div class="toast-icon" v-if="type === 'success'">✓</div>
      <div class="toast-icon" v-else-if="type === 'error'">✕</div>
      <div class="toast-icon" v-else-if="type === 'info'">ℹ</div>
      <div class="toast-content">
        <p>{{ message }}</p>
      </div>
      <button @click="closeToast" class="close-btn" aria-label="Close notification">
        <svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M1 1L11 11M1 11L11 1" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
      </button>
    </div>
  </transition>
</template>

<script setup>
import { ref, watch, defineProps, defineEmits, onUnmounted } from 'vue';

const props = defineProps({
  message: { type: String, required: true },
  type: { type: String, default: 'success' }, // e.g., success, error, info
  duration: { type: Number, default: 4000 } // Duration in ms
});

const emit = defineEmits(['close']);

const visible = ref(true);
let timer = null;

const closeToast = () => {
  clearTimeout(timer);
  visible.value = false;
  emit('close'); // Notify parent it was closed
};

// Automatically close after duration
watch(() => props.message, (newMessage) => {
  if (newMessage) {
    visible.value = true;
    clearTimeout(timer);
    timer = setTimeout(() => {
      closeToast();
    }, props.duration);
  }
}, { immediate: true });

// Ensure timer is cleared if component is unmounted
onUnmounted(() => {
  clearTimeout(timer);
});
</script>

<style scoped>
.toast-notification {
  position: fixed;
  bottom: var(--space-lg);
  right: var(--space-lg);
  padding: var(--space-sm) var(--space-md);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  display: flex;
  align-items: center;
  min-width: 300px;
  max-width: 450px;
  z-index: var(--z-tooltip);
  color: white;
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.toast-notification.success {
  background-color: var(--color-success);
  background: linear-gradient(135deg, var(--color-success), rgba(16, 185, 129, 0.8));
}

.toast-notification.error {
  background-color: var(--color-danger);
  background: linear-gradient(135deg, var(--color-danger), rgba(239, 68, 68, 0.8));
}

.toast-notification.info {
  background-color: var(--color-info);
  background: linear-gradient(135deg, var(--color-info), rgba(59, 130, 246, 0.8));
}

.toast-icon {
  font-size: 1.2rem;
  font-weight: bold;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: var(--space-sm);
  flex-shrink: 0;
}

.toast-content {
  flex-grow: 1;
  padding-right: var(--space-sm);
}

.toast-notification p {
  margin: 0;
  font-weight: 500;
  line-height: 1.4;
}

.close-btn {
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.8);
  cursor: pointer;
  opacity: 0.8;
  padding: var(--space-xs);
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-full);
  transition: all var(--transition-fast);
  flex-shrink: 0;
}

.close-btn:hover {
  opacity: 1;
  background-color: rgba(255, 255, 255, 0.1);
  color: white;
}

/* Transition */
.toast-enter-active,
.toast-leave-active {
  transition: transform var(--transition-normal), opacity var(--transition-normal);
}

.toast-enter-from,
.toast-leave-to {
  transform: translateY(20px);
  opacity: 0;
}
</style> 