import React from "react";
import { ShieldAlert, RefreshCw } from "lucide-react";

export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error("ErrorBoundary caught an unhandled component error:", error, errorInfo);
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-boundary-backdrop">
          <div className="error-boundary-card">
            <div className="error-boundary-icon">
              <ShieldAlert size={32} />
            </div>
            <h2>Something went wrong</h2>
            <p>This view could not be displayed due to a temporary rendering error.</p>
            <button className="primary-button" onClick={this.handleReset}>
              <RefreshCw size={14} />
              Try Again
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
