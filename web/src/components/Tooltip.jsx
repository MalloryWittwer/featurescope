import "./tooltip.css";
import { Component } from "react";

class Tooltip extends Component {
  render() {
    const { imageURL } = this.props;
    return (
      <div className="tooltip invisible" id="tooltip">
        <img src={`${imageURL}`} alt="tooltip" />
        <div id="triangle"></div>
      </div>
    );
  }
}

export default Tooltip;