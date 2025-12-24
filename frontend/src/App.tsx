import { C1Chat, ThemeProvider } from '@thesysai/genui-sdk'
import "@crayonai/react-ui/styles/index.css"
import './App.css'

// Simple wrapper component that mounts the TheSys GenUI chat UI (C1Chat)
// Notes:
// - `C1Chat` is the provided chat UI component from the @thesysai/genui-sdk package.
// - `ThemeProvider` controls the UI theme (e.g., 'dark' or 'light').
// - `apiUrl` is the endpoint the chat UI will call for messages. In development we often
// keep this as '/api/chat' and rely on the Vite proxy (see vite.config.js) to forward
// requests to your FastAPI backend running at http://localhost:8888.


function App() {
  return (
    <div className='app-container'>
      <ThemeProvider mode='dark'>
        <C1Chat apiUrl='/api/chat'/> 
      </ThemeProvider>
    </div>
  )
}

export default App