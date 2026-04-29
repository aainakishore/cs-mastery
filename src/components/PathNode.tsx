import { motion } from 'framer-motion'
import type { Topic, TopicStatus, TopicProgress } from '../content/schema'

interface Props {
  topic: Topic
  status: TopicStatus
  onClick?: () => void
  isActive?: boolean
  color?: string
  progress?: TopicProgress
}

// Topic emoji map — keyed on kebab-case topic id prefix or unit
const TOPIC_EMOJIS: Record<string, string> = {
  // Unit 1 - Foundations
  'linux':            '🐧',
  'git':              '🌿',
  'relational':       '🗄️',
  'embedded':         '💾',
  'time-space':       '⏱️',
  'recursion':        '🔄',
  'memory':           '🧠',
  'pointers':         '📌',
  // Unit 2 - Python
  'python':           '🐍',
  // Unit 3 - TypeScript
  'ts-':              '🔷',
  // Unit 4 - React
  'react':            '⚛️',
  // Unit 5 - Angular
  'angular':          '🔺',
  // Unit 6 - Networking
  'firewalls':        '🛡️',
  'ftp':              '📡',
  'proxies':          '🔀',
  'rpc':              '🔌',
  'websockets':       '🔗',
  'long-polling':     '⏳',
  'rate-limiting':    '🚦',
  'qps':              '📊',
  'load-balancing':   '⚖️',
  // Unit 7 - AI Primer
  'ml-':              '🤖',
  'neural':           '🧬',
  'transformers':     '🔮',
  'llms':             '💬',
  'prompting':        '✨',
  // Unit 8 - DSA Java
  'dsa-java-arrays':  '📋',
  'dsa-java-strings': '🔤',
  'dsa-java-linked':  '⛓️',
  'dsa-java-stacks':  '📚',
  'dsa-java-queues':  '🎫',
  'dsa-java-hashing': '#️⃣',
  'dsa-java-recur':   '🔁',
  'dsa-java-sort':    '🔢',
  'dsa-java-search':  '🔍',
  'dsa-java-binary':  '🌲',
  'dsa-java-trees':   '🌳',
  'dsa-java-heaps':   '⛰️',
  'dsa-java-graphs':  '🕸️',
  'dsa-java-dp':      '💡',
  'dsa-java-tries':   '🔠',
  'dsa-java-sliding': '🪟',
  'dsa-java-two':     '👉',
  // Unit 9 - Scaling
  'caching':          '⚡',
  'sharding':         '🔪',
  'partitioning':     '🗂️',
  'kafka':            '📨',
  'rabbitmq':         '🐰',
  // Unit 10 - Cloud
  'cloud-fund':       '☁️',
  'docker':           '🐳',
  'kubernetes':       '⎈',
  'serverless':       '⚡',
  'cicd':             '🚀',
  'error-log':        '📋',
  // Unit 11 - AI Advanced
  'agents':           '🕵️',
  'rag':              '📖',
  'fine-tuning':      '🎛️',
  'leverage':         '🏋️',
  'ai-image':         '🎨',
  'prompt-eng':       '🧪',
  'llm-ops':          '🏭',
  // Unit 12 - Security
  'security':         '🔒',
  // Unit 13 - System Design
  'system-design':    '🏗️',
  'data-struct':      '📐',
  'distributed':      '🌐',
  'database-int':     '🗃️',
  'observability':    '👁️',
  'api-design':       '🔌',
  'caching-adv':      '⚡',
  // Unit 14 - Java Advanced
  'java-multi':       '🧵',
  'java-conc':        '⚙️',
  // Unit 15 - Finance
  'fin-stock':        '📈',
  'fin-tech':         '📉',
  'fin-fund':         '💰',
  'fin-opt':          '🎲',
  'fin-mut':          '🏦',
  'fin-per':          '💳',
  'fin-mac':          '🌍',
  // Unit 16 - Advanced
  'sql-adv':          '🔗',
  'git-adv':          '🌿',
  // Unit 17 - Tooling
  'pycharm':          '🛠️',
  // Unit 18 - AWS
  'aws-prac':         '☁️',
  'aws-mas':          '🏆',
  'aws-sqs':          '📬',
  'aws-lambda':       '⚡',
  'aws-vpc':          '🔒',
  'aws-ecs':          '🐳',
  'aws-rds':          '🗄️',
}

function getTopicEmoji(id: string): string {
  for (const [prefix, emoji] of Object.entries(TOPIC_EMOJIS)) {
    if (id.startsWith(prefix)) return emoji
  }
  return '📗'
}

export function PathNode({ topic, status, onClick, isActive, color = '#6366f1', progress }: Props) {
  const clickable = status !== 'locked'
  const emoji = getTopicEmoji(topic.id)

  const bg = status === 'locked' ? 'transparent' : status === 'learned' ? color : 'transparent'
  const border = status === 'locked' ? 'var(--border)' : color

  // Derive quadrant completions (0-4 filled quarters of the donut ring)
  const quizPassed = progress?.quizHistory?.some(q => q.score >= 0.8) ?? false
  const projectDone = progress?.projectComplete ?? false
  const topicAccessed = status !== 'locked'
  const flashcardsDone = quizPassed
  const segments = [topicAccessed, flashcardsDone, quizPassed, projectDone]
  const filledCount = segments.filter(Boolean).length

  // SVG donut ring — outer circle with 4 arcs
  const RADIUS = 30
  const CIRCUMFERENCE = 2 * Math.PI * RADIUS
  const segLen = CIRCUMFERENCE / 4
  const GAP = 3

  return (
    <div className="flex flex-col items-center gap-1 w-20">
      <div className="relative" style={{ width: 72, height: 72 }}>
        {/* Outer donut segments */}
        <svg
          width="72" height="72" viewBox="0 0 72 72"
          style={{ position: 'absolute', top: 0, left: 0, transform: 'rotate(-90deg)' }}
        >
          {segments.map((filled, i) => {
            const offset = (i * segLen) + i * GAP / (2 * Math.PI * RADIUS) * CIRCUMFERENCE
            return (
              <circle
                key={i}
                cx="36" cy="36" r={RADIUS}
                fill="none"
                stroke={filled ? color : (status === 'locked' ? 'var(--border)' : color + '30')}
                strokeWidth="5"
                strokeDasharray={`${segLen - 4} ${CIRCUMFERENCE - segLen + 4}`}
                strokeDashoffset={-(offset)}
                strokeLinecap="round"
                opacity={filled ? 1 : 0.35}
              />
            )
          })}
        </svg>

        {/* Inner circle with emoji */}
        <motion.button
          onClick={clickable ? onClick : undefined}
          disabled={!clickable}
          animate={
            status === 'available'
              ? { scale: [1, 1.06, 1], transition: { repeat: Infinity, duration: 2.5 } }
              : isActive ? { scale: 1.1 } : { scale: 1 }
          }
          whileTap={clickable ? { scale: 0.9 } : {}}
          className="absolute flex items-center justify-center rounded-full text-2xl"
          style={{
            top: 9, left: 9,
            width: 54, height: 54,
            background: bg || (status === 'learned' ? color : status === 'available' ? color + '22' : 'var(--bg-card)'),
            border: `2px solid ${border}`,
            cursor: clickable ? 'pointer' : 'default',
            opacity: status === 'locked' ? 0.4 : 1,
            boxShadow: status !== 'locked' ? `0 0 14px ${color}50` : 'none',
            fontSize: status === 'locked' ? '1.1rem' : '1.3rem',
            filter: status === 'locked' ? 'grayscale(80%)' : 'none',
          }}
        >
          {emoji}
        </motion.button>

        {/* Learned checkmark badge */}
        {status === 'learned' && filledCount >= 3 && (
          <div
            className="absolute text-white text-xs font-bold rounded-full flex items-center justify-center"
            style={{
              bottom: -2, right: -2, width: 18, height: 18,
              background: color,
              border: '2px solid var(--bg-app)',
              fontSize: 10,
            }}
          >✓</div>
        )}
      </div>

      <span
        className="text-xs font-semibold text-center leading-tight line-clamp-2"
        style={{
          color: status === 'locked' ? 'var(--text-subtle)' : 'var(--text-primary)',
          maxWidth: 72,
        }}
      >
        {topic.title}
      </span>
    </div>
  )
}
