import React, { Component } from "react";
import Point from "./Point";
import Tooltip from "./Tooltip";

class Canvas extends Component {
  constructor(props) {
    super(props);
    this.state = { toolTipImageUrl: null };
  }

  keyPressListener = (e) => {
    if (e.code === "ControlLeft") {
      document.getElementById("canvas").style.cursor = "crosshair";
    }
  };

  keyUpListener = (e) => {
    document.getElementById("canvas").style.cursor = "grab";
  };

  handleMouseEnter = (e) => {
    document.addEventListener("keydown", this.keyPressListener);
    document.addEventListener("keyup", this.keyUpListener);
  };

  handleMouseLeave = (e) => {
    document.removeEventListener("keydown", this.keyPressListener);
    document.removeEventListener("keyup", this.keyUpListener);
  };

  fetchToolTipImage = async (imageID) => {
    if (!imageID) {
      return;
    }
    fetch(`http://localhost:8000/images/${imageID}`)
      .then((r) => r.json())
      .then((content) => {
        const imageUrl = `data:image/png;base64,${content.image}`;
        this.setState({ toolTipImageUrl: imageUrl });
      });
  };

  setToolTipImageID = (toolTipImageID) => {
    const toolTipImageUrl = this.fetchToolTipImage(toolTipImageID);
    this.setState({ toolTipImageUrl });
  };

  render() {
    const { pointSize, displayDataSet } = this.props;
    const { toolTipImageUrl } = this.state;
    if (displayDataSet) {
      return (
        <div
          id="canvas"
          onMouseEnter={this.handleMouseEnter}
          onMouseLeave={this.handleMouseLeave}
        >
          {displayDataSet.map((pointData) => {
            const { id, x, y, thumbnail } = pointData;
            return (
              <Point
                actionFnct={this.setToolTipImageID}
                key={id}
                xPos={x}
                yPos={y}
                size={pointSize}
                id={id}
                thumbnail={thumbnail}
              />
            );
          })}
          <Tooltip imageURL={toolTipImageUrl} />
        </div>
      );
    } else {
      return <div id="canvas"></div>;
    }
  }
}

export default Canvas;
