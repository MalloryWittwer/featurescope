import "./dropdown.css";
import React, { Component } from "react";
import Select from "react-select";

const customStyles = {
  option: (provided, state) => ({
    ...provided,
    borderBottom: "1px solid aliceblue",
    color: "aliceblue",
    background: state.isFocused ? "#434C56" : "none",
  }),

  indicatorsContainer: (provided) => ({
    ...provided,
    background: "aliceblue",
  }),

  valueContainer: (provided) => ({
    ...provided,
    background: "#16181b",
    border: "1px solid #aaaaaa",
  }),

  indicatorSeparator: (provided) => ({
    ...provided,
    background: "#999999",
  }),

  singleValue: (provided) => ({
    ...provided,
    color: "aliceblue",
  }),

  menu: (provided) => ({
    ...provided,
    background: "black",
    width: 200,
  }),

  menuPortal: base => ({ ...base, zIndex: 9999 }),
};

class Dropdown extends Component {
  handleUpdate = (option) => {
    this.props.actionFnct(option.value);
  };

  render() {
    return (
      <div className="range-container">
        <label htmlFor="selector">{this.props.label}</label>
        <Select
          options={this.props.options}
          styles={customStyles}
          onChange={this.handleUpdate}
          id="selector"
          name="selector"
          // defaultValue={this.props.defaultValue}
          menuPortalTarget={document.body} 
        />
      </div>
    );
  }
}

export default Dropdown;
