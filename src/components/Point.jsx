import "./point.css";
import { Component } from "react";

class Point extends Component {
  handleMouseEnter = (e) => {
    const { id, yPos, xPos, size, actionFnct } = this.props;
    e.preventDefault();
    e.currentTarget.classList.add("hovered-point");

    actionFnct(id);

    const tooltip = document.getElementById("tooltip");
    if (tooltip != null) {
      tooltip.classList.remove("invisible");
      tooltip.style.top = `${Number.parseInt(yPos, 10) - 220 - size / 2}px`;
      tooltip.style.left = `${Number.parseInt(xPos, 10) - 102}px`;
    }

    const triangle = document.getElementById("triangle");
    if (triangle != null) {
      triangle.style.borderTopColor = "#282c34";
    }
  };

  handleMouseLeave = (e) => {
    e.preventDefault();
    e.currentTarget.classList.remove("hovered-point");
    document.getElementById("tooltip").classList.add("invisible");
  };

  render = () => {
    const { yPos, xPos, size, thumbnail } = this.props;
    const imageUrl = `data:image/png;base64,${thumbnail}`;
    return (
      <div
        className="point"
        onMouseEnter={this.handleMouseEnter}
        onMouseLeave={this.handleMouseLeave}
        style={{
          top: `${Number.parseInt(yPos, 10) - size / 2}px`,
          left: `${Number.parseInt(xPos, 10) - size / 2}px`,
          width: `${size}px`,
          height: `${size}px`,
          fontSize: `${0.5 * size}px`,
          backgroundImage: `url(${imageUrl})`,
        }}
      ></div>
    );
  };
}

export default Point;
